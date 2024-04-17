from aiokafka import AIOKafkaProducer
import asyncio

from app import settings

event_loop = asyncio.get_event_loop()


class AIOProducer(object):
    def __init__(self):
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVICE,
            loop=event_loop
        )
        self.__produce_topic = settings.PRODUCE_TOPIC

    async def start(self) -> None:
        await self.__producer.start()

    async def stop(self) -> None:
        await self.__producer.stop()

    async def send(self, value: bytes) -> None:
        await self.start()
        try:
            await self.__producer.send(
                topic=self.__produce_topic,
                value=value
            )
        finally:
            await self.stop()

    async def send_and_wait(self, value: bytes) -> None:
        await self.start()
        try:
            await self.__producer.send_and_wait(
                topic=self.__produce_topic,
                value=value
            )
        finally:
            await self.stop() 


def get_producer() -> AIOProducer:
    return AIOProducer()