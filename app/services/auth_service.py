from app.db.connection import users_collection
from passlib.context import CryptContext
from fastapi import HTTPException
from app.models.user_model import UserRegister, OAuthLogin
from bson.objectid import ObjectId
from datetime import datetime, timezone
from app.utils.jwt_auth import create_access_token, create_refresh_token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
GOOGLE_CLIENT_ID = "414871766869-9haftr4td63vrg7p8ef4ko4bgdhhedo1.apps.googleusercontent.com"
GITHUB_USER_API = "https://api.github.com/user"
LINKEDIN_USER_API = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def register_user(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(user.password)
    user_doc = {
        "email": user.email,
        "password": hashed_password,
        "name": user.name,
        "payment": {
            "payment_status": user.payment.payment_status,
            "plans": [plan.model_dump() for plan in user.payment.plans]
        } if user.payment else None,
        "segmentation_data": [
            {
                "session_id": seg.session_id,
                "config_data": [
                    {
                        "config_name": item.config_name,
                        "config_model": item.config_model
                    } for item in seg.config_data
                ]
            } for seg in user.segmentation_data
        ] if user.segmentation_data else [],
        "auth_provider": "email",
        "created_at": datetime.now(timezone.utc)
    }
    users_collection.insert_one(user_doc)
    token = create_access_token({"email": user.email, "user_id": str(user_doc.get("_id"))})
    return {"message": "User registered successfully", "token": token}

def login_user(email: str, password: str):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if user.get("auth_provider") != "email":
        raise HTTPException(status_code=400, detail="Use your social login provider")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"email": user["email"], "name": user["name"],  "id": str(user["_id"])})
    refresh_token = create_refresh_token({"email": user["email"], "name": user["name"], "id": str(user["_id"])})
    message = "Login Successful"
    
    return message, access_token, refresh_token

def oauth_login_user(user: OAuthLogin):
    provider = user.provider.lower()

    # Extract user identity from token (if needed)
    email = user.email
    name = user.name

    if provider == "google":
        try:
            idinfo = id_token.verify_oauth2_token(
                user.oauth_token,
                google_requests.Request(),
                GOOGLE_CLIENT_ID
            )
            email = idinfo.get("email")
            name = idinfo.get("name")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")

    elif provider == "github":
        try:
            headers = {"Authorization": f"Bearer {user.oauth_token}"}
            res = requests.get(GITHUB_USER_API, headers=headers)
            res.raise_for_status()
            profile = res.json()
            email = profile.get("email")
            name = profile.get("name") or profile.get("login")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid GitHub token: {str(e)}")

    elif provider == "linkedin":
        try:
            headers = {"Authorization": f"Bearer {user.oauth_token}"}
            email_res = requests.get(LINKEDIN_USER_API, headers=headers)
            email_res.raise_for_status()
            email_json = email_res.json()
            email = email_json["elements"][0]["handle~"]["emailAddress"]

            profile_res = requests.get("https://api.linkedin.com/v2/me", headers=headers)
            profile_res.raise_for_status()
            profile = profile_res.json()
            first = profile.get("localizedFirstName", "")
            last = profile.get("localizedLastName", "")
            name = f"{first} {last}".strip()
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid LinkedIn token: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

    if not email:
        raise HTTPException(status_code=400, detail="Could not extract email from token")

    # Check if user already exists
    existing_user = users_collection.find_one({
        "email": email,
        "auth_provider": provider
    })

    if existing_user:
        token = create_access_token({
            "email": email,
            "user_id": str(existing_user["_id"])
        })
        return {
            "message": "OAuth login successful",
            "token": token
        }

    # Register new user
    user_doc = {
        "email": email,
        "name": name or email.split("@")[0],
        "auth_provider": provider,
        "created_at": datetime.utcnow()
    }
    result = users_collection.insert_one(user_doc)
    token = create_access_token({
        "email": email,
        "user_id": str(result.inserted_id)
    })

    return {
        "message": "Social user registered and logged in",
        "token": token
    }