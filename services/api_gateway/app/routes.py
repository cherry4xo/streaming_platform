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


async def start_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVICE)
    await producer.start()
    return producer


async def main() -> None:
    consumer = await start_consumer()
    producer = await start_producer()
    try:
        for message in consumer:
            decoded_message = json.loads(message.value)
            credentials = CredentialsSchema(email=decoded_message["email"], password=decoded_message["password"])
            user = await authenticate(credentials=credentials)

            if not user:
                raise HTTPException(
                    status_code=400,
                    detail="Incorrect email or password"
                )
            
            message_to_dump = {
                "access_token": create_access_token(data={"user_uuid": str(user.uuid)}),
                "refresh_token": create_refresh_token(data={"user_uuid": str(user.uuid)}),
                "token_type": "bearer"
            }

            value_to_send = json.dumps(message_to_dump).encode(encoding="utf-8")
            await producer.send(value=value_to_send, topic=settings.PRODUCE_TOPIC)

    finally:
        await consumer.stop()
        await producer.stop()


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


@router.post("/refresh", response_model=JWTAccessToken)
async def refresh(token: str):
    user = await get_current_user(token=token)

    return {
        "access_token": create_access_token(data={"user_uuid": str(user.uuid)}),
        "token_type": "bearer"
    }
