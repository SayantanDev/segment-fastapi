from app.db.connection import users_collection
from passlib.context import CryptContext
from fastapi import HTTPException
from app.models.user_model import UserRegister, OAuthLogin
from bson.objectid import ObjectId
from datetime import datetime, timezone
from app.utils.jwt_auth import create_access_token, create_refresh_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    existing_user = users_collection.find_one({
        "email": user.email,
        "auth_provider": user.provider.lower()
    })

    if existing_user:
        token = create_access_token({"email": user.email, "user_id": str(existing_user["_id"])})
        return {"message": "OAuth login successful", "token": token}

    user_doc = {
        "email": user.email,
        "name": user.name or user.email.split("@")[0],
        "auth_provider": user.provider.lower(),
        "created_at": datetime.utcnow()
    }
    result = users_collection.insert_one(user_doc)
    token = create_access_token({"email": user.email, "user_id": str(result.inserted_id)})
    return {"message": "Social user registered and logged in", "token": token}

