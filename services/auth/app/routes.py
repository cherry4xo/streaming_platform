from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends

from app.schemas import JWTAccessToken, JWTRefreshToken, JWTToken, CredentialsSchema
from app.models import User
from app.utils.contrib import authenticate, get_current_user
from app.utils.jwt import create_access_token, create_refresh_token
from app import settings
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/access-refresh-token", response_model=JWTToken)
async def login_access_refresh_token(credentials: OAuth2PasswordRequestForm = Depends()):
    credentials = CredentialsSchema(email=credentials.username, password=credentials.password)
    user = await authenticate(credentials=credentials)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    
    return {
        "access_token": create_access_token(data={"user_uuid": str(user.uuid)}),
        "refresh_token": create_refresh_token(data={"user_uuid": str(user.uuid)}),
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=JWTRefreshToken)
async def refresh(refresh_token: str):
    pass
       
