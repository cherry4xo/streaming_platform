import json
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.schemas import JWTAccessToken, JWTRefreshToken, JWTToken, CredentialsSchema
from app.models import User
from app.utils.contrib import authenticate, get_current_user
from app.utils.jwt import create_access_token, create_refresh_token
from app import settings
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


async def start_consumer() -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        bootstrap_servers=settings.BOOTSTRAP_SERVICE,
    )
    consumer.subscribe(topics=[settings.CONSUME_TOPIC])
    await consumer.start()
    return consumer


async def send_producer(message: str, topic: str = None) -> AIOKafkaProducer:
    topic = topic or settings.PRODUCE_TOPIC
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.BOOTSTRAP_SERVICE,
    )
    await producer.start()
    try:    
        await producer.send(topic=topic, value=message) 
    finally:
        await producer.stop()


async def main() -> None:
    consumer = await start_consumer()
    try:
        for message in consumer:
            decoded_message = json.loads(message.value)
            


@router.post("/access-token", response_model=JWTToken)
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
       
