from aio_pika import connect, Message, ExchangeType, DeliveryMode

import asyncio

from datetime import datetime

import json

import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

# FIXME: Move this to a single configuration file where it is being set
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")
RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/{RABBITMQ_VHOST}"
)


class PublishMonitoringEvent:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.topic_logs_exchange = None
        self.is_connected = False

    async def connect(self):
        if not self.is_connected:
            self.connection = await connect(RABBITMQ_URL)
            self.channel = await self.connection.channel()
            self.topic_logs_exchange = await self.channel.declare_exchange(
                "model_monitoring_exchange", ExchangeType.TOPIC
            )
            self.is_connected = True
            return self

    async def publish_event(self, event_type: str, module_name: str, event_data: dict):
        if not self.is_connected:
            await self.connect()

        routing_key = f"monitoring.{event_type}.{module_name}"
        message_body = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "module_name": module_name,
            "data": event_data,
        }
        message = Message(
            json.dumps(message_body).encode("utf-8"),
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await self.topic_logs_exchange.publish(message, routing_key=routing_key)

        print(f" [x] Sent {message!r}")

    async def close(self):
        """Close the RabbitMQ connection and channel safely."""
        if self.is_connected:
            if self.channel is not None and not self.channel.is_closed:
                await self.channel.close()
                self.channel = None

            if self.connection is not None and not self.connection.is_closed:
                await self.connection.close()
                self.connection = None

            self.topic_logs_exchange = None
            self.is_connected = False
