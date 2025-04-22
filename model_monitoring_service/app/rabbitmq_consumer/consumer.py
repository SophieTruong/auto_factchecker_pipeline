import asyncio

import aio_pika
from aio_pika import ExchangeType
from aio_pika.pool import Pool
from aio_pika.abc import AbstractRobustConnection, AbstractIncomingMessage

from database.mongodb import MongoDBManager
from monitoring_service import MonitoringService

import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")
RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/{RABBITMQ_VHOST}"
)


class MonitoringConsumer:
    def __init__(
        self,
        db_manager: MongoDBManager,
        monitoring_service: MonitoringService,
        queue_name: str = "logging_queue",
        exchange_name: str = "model_monitoring_exchange",
        binding_keys: list[str] = None,
    ):
        self.queue_name = queue_name

        self.exchange_name = exchange_name

        self.binding_keys = binding_keys or [
            "monitoring.complete.evidence_retrieval",
            "monitoring.created.claim_annotation",
        ]

        self.mongodb_manager = db_manager

        self.monitoring_service = monitoring_service

    async def consume(self, channel: aio_pika.Channel):

        await channel.set_qos(10)

        exchange = await channel.declare_exchange(
            self.exchange_name, ExchangeType.TOPIC
        )

        queue = await channel.declare_queue(self.queue_name, durable=True)

        for key in self.binding_keys:

            await queue.bind(exchange, key)

        print(" [*] Waiting for messages.")

        async with queue.iterator() as queue_iter:

            async for message in queue_iter:

                await self.process_message(message)

    async def process_message(self, message: AbstractIncomingMessage):
        """Process individual messages"""

        async with message.process():
            # Parse and validate
            parsed_message = self.monitoring_service.parse_message_body(message.body)

            if not parsed_message or not self.monitoring_service.validate_message(
                parsed_message
            ):

                print("Invalid message format")

                return

            event_type = parsed_message["event_type"]

            module_name = parsed_message["module_name"]

            # Route to appropriate handler
            handlers = {
                (
                    "complete",
                    "evidence_retrieval",
                ): self.monitoring_service.handle_evidence_retrieval_metrics,
                (
                    "created",
                    "claim_annotation",
                ): self.monitoring_service.handle_claim_annotation_metrics,
            }

            handler = handlers.get((event_type, module_name))

            if handler:

                success = await handler(self.mongodb_manager, parsed_message)

                print(
                    f"Message processing {'succeeded' if success else 'failed'}: {event_type}.{module_name}"
                )

            else:

                print(f"Unsupported event type: {event_type} or module: {module_name}")


async def main():

    # Initialize dependencies
    db_manager = MongoDBManager()

    monitoring_service = MonitoringService()

    try:
        # Connect to DB
        db_manager.connect_to_db()

        # Initialize consumer
        consumer = MonitoringConsumer(
            db_manager=db_manager, monitoring_service=monitoring_service
        )

        async def get_connection() -> AbstractRobustConnection:

            return await aio_pika.connect_robust(RABBITMQ_URL)

        connection_pool: Pool = Pool(get_connection, max_size=2)

        async def get_channel() -> aio_pika.Channel:

            async with connection_pool.acquire() as connection:

                return await connection.channel()

        channel_pool: Pool = Pool(get_channel, max_size=10)

        # Use connection and channel pools with context managers
        async with connection_pool, channel_pool:

            async with channel_pool.acquire() as channel:

                await consumer.consume(channel)

    except asyncio.CancelledError:

        print("Consumer cancelled")

    except Exception as e:

        print(f"Consumer error: {e}")

    finally:
        # Ensure cleanup
        db_manager.close()


if __name__ == "__main__":

    asyncio.run(main())
