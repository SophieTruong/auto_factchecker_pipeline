from aio_pika import connect, Message, ExchangeType
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
)
import json
import uuid
from models.semantic_search_input import SemanticSearchInput
import asyncio
from typing import MutableMapping

from utils.app_logging import logger

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


class EvidenceRetrievalRpcClient:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue

    def __init__(self):
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.is_connected = False
        self.consumer_tag = None

    async def connect(self):
        if self.is_connected:
            return self

        try:
            self.connection = await connect(RABBITMQ_URL)

            logger.info(f"Connected to RabbitMQ at {RABBITMQ_URL}")

            self.channel = await self.connection.channel()

            await self.channel.set_qos(prefetch_count=10)

            logger.info(f"Channel created")

            self.callback_queue = await self.channel.declare_queue(exclusive=True)

            # Store the consumer tag returned from consume
            self.consumer_tag = await self.callback_queue.consume(
                self.on_response, no_ack=True
            )

            logger.info(
                f"Callback queue created with consumer tag: {self.consumer_tag}"
            )

            self.is_connected = True

            return self

        except Exception as e:

            logger.error(f"Error connecting to RabbitMQ: {e}")

            raise e

    async def on_response(self, message: AbstractIncomingMessage):
        if message.correlation_id is None:

            logger.info(f"Bad message {message!r}")

            return

        try:
            future: asyncio.Future = self.futures.pop(message.correlation_id)

            future.set_result(message.body)

        except KeyError as e:
            logger.info(f"KeyError: {e}")

            logger.warning(
                f"Received response for unknown correlation_id: {message.correlation_id}"
            )

            return

        except Exception as e:

            logger.error(f"Error processing response: {e}")

            return

    async def get_search_result(self, claim: SemanticSearchInput):
        try:
            if not self.is_connected:
                await self.connect()

            correlation_id = str(uuid.uuid4())

            logger.info(
                f"A correlation_id is generated for get_search_result: {correlation_id}"
            )

            loop = asyncio.get_running_loop()

            future = loop.create_future()

            self.futures[correlation_id] = future

            # Publish message
            message = Message(
                body=json.dumps(
                    {"claim": claim.model_dump(), "correlation_id": correlation_id}
                ).encode(),
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            )

            # Log more details about the message
            logger.info(f"Publishing message to queue: rpc_evidence_retrieval_queue")

            logger.info(f"Message reply_to: {self.callback_queue.name}")

            # Publish with confirmation
            await self.channel.default_exchange.publish(
                message, routing_key="rpc_evidence_retrieval_queue"
            )

            logger.info(f"Published message successfully")

            # Set a timeout for the future
            try:
                result = await asyncio.wait_for(future, timeout=30.0)

                return result

            except asyncio.TimeoutError:
                logger.error(
                    f"Timeout waiting for response with correlation_id: {correlation_id}"
                )

                self.futures.pop(correlation_id, None)

                raise TimeoutError(
                    "No response received from evidence retrieval service"
                )

        except Exception as e:
            logger.error(f"Error in get_search_result: {e}")
            raise

    async def close(self):
        """Close the RabbitMQ connection and channel safely."""
        if self.is_connected:
            try:
                # Cancel consumer if active
                if (
                    hasattr(self, "callback_queue")
                    and self.callback_queue is not None
                    and self.consumer_tag is not None
                ):
                    await self.callback_queue.cancel(self.consumer_tag)
                    logger.info(f"Canceled consumer with tag: {self.consumer_tag}")

                # Close channel if open
                if (
                    hasattr(self, "channel")
                    and self.channel is not None
                    and not self.channel.is_closed
                ):
                    await self.channel.close()

                # Close connection if open
                if (
                    hasattr(self, "connection")
                    and self.connection is not None
                    and not self.connection.is_closed
                ):
                    await self.connection.close()

                # Clear any pending futures
                for future in self.futures.values():
                    if not future.done():
                        future.set_exception(Exception("Connection closed"))
                self.futures.clear()

                self.is_connected = False
                self.consumer_tag = None
                logger.info("RabbitMQ connection closed successfully")

            except Exception as e:
                logger.error(f"Error closing RabbitMQ connection: {e}")
                raise e
