from datetime import date

from fastapi import APIRouter, HTTPException, Depends

from app.schemas import UserCreate, UserOut
from app.models import User
from app.utils import password
from app import settings


router = APIRouter()


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    user_in: UserCreate
):
    user = await User.get_by_email(email=user_in.email)

    if user is not None:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists"
        )
    
    db_user = await User.create(**user_in.model_dump())
    return db_user


@router.get("/me", response_model=UserOut, status_code=200)
async def get_user_me(
    token: str
):
    pass
    # TODO make kafka sending