import json
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, Security

from app.schemas import JWTAccessToken, JWTRefreshToken, JWTToken, CredentialsSchema
from app.models import User
from app.utils.contrib import authenticate, validate_refresh_token, reusable_oauth2, refresh_oauth2, get_current_user
from app.utils.jwt import create_access_token, create_refresh_token
from app.redis import r, ping_redis_connection
from app import settings
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/access-token", response_model=JWTToken)
async def login_access_token(credentials: OAuth2PasswordRequestForm = Depends()):
    credentials = CredentialsSchema(email=credentials.username, password=credentials.password)
    user = await authenticate(credentials=credentials)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": create_access_token(data={"user_uuid": str(user.uuid)}, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(data={"user_uuid": str(user.uuid)}, expires_delta=refresh_token_expires),
        "token_type": "bearer"
    }


@router.post("/refresh-token", response_model=JWTRefreshToken)
async def login_refresh_token(credentials: OAuth2PasswordRequestForm = Depends()):
    credentials = CredentialsSchema(email=credentials.username, password=credentials.password)
    user = await authenticate(credentials=credentials)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    
    return {
        "refresh_token": create_refresh_token(data={"user_uuid": str(user.uuid)}, expires_delta=refresh_token_expires),
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=JWTAccessToken)
async def refresh_token(
    current_user: User = Depends(validate_refresh_token)
):
    refresh_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"user_uuid": str(current_user.uuid), "expires_delta": refresh_token_expires})
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


#TODO complete auth in krakend
@router.get("/validate", status_code=200)
async def validate_access_token(
    token: str = Security(reusable_oauth2)
):
    return await get_current_user(token=token)


@router.get("/symmetric.json", status_code=200)
async def get_kid():
    return {
        "Keys": [
            {
                "kid": "sim2",
                "kty": "oct",
                "k": f"{settings.SECRET_KEY}",
                "alg": "HS256"
            }
        ]
    }
    
    
