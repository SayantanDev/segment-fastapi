from fastapi import APIRouter, Response
from app.models.user_model import UserRegister, UserLogin, OAuthLogin, LoginResponse
from app.services.auth_service import register_user, login_user, oauth_login_user

auth_router = APIRouter()

@auth_router.post("/register")
def register(user: UserRegister):
    return register_user(user)

# @auth_router.post("/login")
# def login(user: UserLogin):
#     return login_user(user.email, user.password)
# =======================================================
@auth_router.post("/login")
def login(user: UserLogin, response: Response):
    message, access_token, refresh_token = login_user(user.email, user.password)

    # Set tokens in custom headers
    response.headers["X-Access-Token"] = access_token
    response.headers["X-Refresh-Token"] = refresh_token

    return message

@auth_router.post("/oauth-login")
def oauth_login(user: OAuthLogin):
    return oauth_login_user(user)
