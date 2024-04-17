import json
from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition

from app.schemas import UserCreate, UserOut
from app.models import User
from app.utils import password
from app.producer import AIOProducer, get_producer
from app import settings


router = APIRouter()


async def start_consumer() -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        bootstrap_servers=settings.BOOTSTRAP_SERVICE,
    )
    consumer.subscribe(topics=[settings.CONSUME_TOPIC])
    await consumer.start()
    return consumer


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    user_in: UserCreate,
):
    user = await User.get_by_email(email=user_in.email)

    if user is not None:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists"
        )
    
    db_user = await User.create(user_in)
    return db_user


@router.get("/me", response_model=UserOut, status_code=200)
async def get_user_me(
    token: str,
    producer: AIOProducer = Depends(get_producer)
):
    token = {"token": token}
    value = json.dumps(token).encode(encoding="utf-8")
    user_id = await producer.send(value=value)

    # consumer = await start_consumer()

    user = await User.get_by_uuid(uuid=user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="The user with this uuid does not exist"
        )
    return user

