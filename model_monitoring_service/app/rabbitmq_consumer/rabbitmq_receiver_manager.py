import asyncio

from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel,
    AbstractExchange,
    AbstractQueue,
    AbstractIncomingMessage,
)

from monitoring_service import MonitoringService

from database.mongodb import MongoDBManager
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

# More fine grained setting of database connection parameters
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")
RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/{RABBITMQ_VHOST}"
)


class RabbitMqReceiverManager:
    def __init__(self):
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractRobustChannel | None = None
        self.topic_logs_exchange: AbstractExchange | None = None
        self.queue: AbstractQueue | None = None
        self.is_connected = False

        self.monitoring_service = MonitoringService()
        self.mongodb_manager = MongoDBManager()

        # TODO: Connect to MongoDB, and get the database

    def connect_to_mongodb(self):
        # Connect to MongoDB first
        print("Connecting to MongoDB...")
        self.mongodb_manager.connect_to_db()
        db = self.mongodb_manager.get_db()
        print(f"Connected to MongoDB database: {db.name}")

    async def connect(self):
        if not self.is_connected:
            # Connect to MongoDB first
            self.connect_to_mongodb()

            print("Connecting to RabbitMQ...")
            # Perform connection
            self.connection = await connect_robust(
                RABBITMQ_URL, loop=asyncio.get_running_loop()
            )

            # Create a channel
            self.channel = await self.connection.channel()

            # Declare the exchange
            self.topic_logs_exchange = await self.channel.declare_exchange(
                "model_monitoring_exchange", ExchangeType.TOPIC
            )

            # Declare the queue
            self.queue = await self.channel.declare_queue("logging_queue", durable=True)

            # Prioritize the topics to process
            binding_keys = [
                "monitoring.complete.evidence_retrieval",
                "monitoring.created.claim_annotation",
            ]

            for key in binding_keys:
                await self.queue.bind(self.topic_logs_exchange, key)

            print(" [*] Waiting for messages.")

            self.is_connected = True

            return self

    async def receive_message(self):
        """Receive messages from the queue."""
        if not self.is_connected:
            await self.connect()

        async with self.queue.iterator() as queue_iter:
            message: AbstractIncomingMessage
            async for message in queue_iter:
                async with message.process() as processed_message:
                    print(f" [x] Received {processed_message.body!r}")

                    # Process the message
                    await self.process_message(processed_message)

    async def process_message(self, processed_message):
        """Process the message using the service layer."""

        # Parse and validate the message using the service
        parsed_message = self.monitoring_service.parse_message_body(
            processed_message.body
        )

        # If parsing failed, log and return
        if parsed_message is None:
            print("Failed to parse message, skipping")
            return

        # Validate the message structure
        if not self.monitoring_service.validate_message(parsed_message):
            print("Invalid message format, skipping")
            return

        # Get the event type and module name
        event_type = parsed_message["event_type"]
        module_name = parsed_message["module_name"]

        # Route to appropriate handler based on event type and module
        success = False
        if event_type == "complete" and module_name == "evidence_retrieval":
            print(f" [x] Processing evidence retrieval metrics: {parsed_message!r}")
            success = await self.monitoring_service.handle_evidence_retrieval_metrics(
                self.mongodb_manager, parsed_message
            )
        elif event_type == "created" and module_name == "claim_annotation":
            print(f" [x] Processing claim annotation metrics: {parsed_message!r}")
            success = await self.monitoring_service.handle_claim_annotation_metrics(
                self.mongodb_manager, parsed_message
            )
        else:
            print(f"Unsupported event type: {event_type} or module: {module_name}")

        if success:
            print(f"Successfully processed message: {event_type}.{module_name}")
        else:
            print(f"Failed to process message: {event_type}.{module_name}")

    async def close(self):
        """Close the RabbitMQ connection and channel safely."""
        if self.is_connected:
            if self.channel is not None and not self.channel.is_closed:
                await self.channel.close()
                self.channel = None

            if self.connection is not None and not self.connection.is_closed:
                await self.connection.close()
                self.connection = None

            # Close MongoDB connection
            self.mongodb_manager.close()

            self.is_connected = False
