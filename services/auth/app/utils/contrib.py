from typing import Optional
import jwt
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer

from starlette.status import HTTP_403_FORBIDDEN

from app.models import User
from app.schemas import JWTTokenPayload, CredentialsSchema
from app.utils import password
from app.utils.jwt import ALGORITHM
from app import settings


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=settings.LOGIN_URL,
)

async def get_current_user(token: str = Security(reusable_oauth2)) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = JWTTokenPayload(**payload)
    except jwt.PyJWTError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")
    
    user = await User.filter(uuid=token_data.user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


async def get_current_admin(current_user: User = Security(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=400,
            detail="Current user does not have enough privileges"
        )


async def authenticate(credentials: CredentialsSchema) -> User | None:
    if credentials.email:
        user = await User.get_by_email(email=credentials.email)
    else:
        return None
    
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist"
        )
    
    verified, updated_password_hash = password.verify_and_update_password(credentials.password, user.password_hash)

    if not verified:
        return None
    
    if updated_password_hash is not None:
        user.password_hash = updated_password_hash
        await user.save()

    return user