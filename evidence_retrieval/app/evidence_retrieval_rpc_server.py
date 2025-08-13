import asyncio
import json

from aio_pika import Message

from rabbitmq_connection_pool import rabbitmq_pool

from services import SemanticSearchService

from model import Claim

from utils import logger

from metric_calculator import compute_metrics

from publish_monitoring_event import PublishMonitoringEvent

import os
import dotenv

# Import the DateTimeEncoder
from web_search_retrieval import DateTimeEncoder

dotenv.load_dotenv(dotenv.find_dotenv())

RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")
RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/{RABBITMQ_VHOST}"
)


async def main():
    logger.info("Starting queue consumer")

    # 1. Initialize Semantic search service
    semantic_search_service = SemanticSearchService()

    publish_monitoring_event = PublishMonitoringEvent()

    logger.info("Initialized Semantic search service")

    # 2. Create connection to rabbitmq
    # Wrap a connection pool around the consumer code: 1 connection
    async with rabbitmq_pool.channel_pool.acquire() as channel:

        await channel.set_qos(10)

        queue = await channel.declare_queue(
            "rpc_evidence_retrieval_queue",
            durable=True,  # Must match the durable=true in definitions.json
            auto_delete=False,  # Must match auto_delete=false in definitions.json
        )

        logger.info(f"Queue created: {queue.name}")

        logger.info(" [x] Awaiting RPC requests for evidence retrieval")

        async with queue.iterator() as qiterator:

            async for message in qiterator:

                try:

                    async with message.process(requeue=False):

                        assert message.reply_to is not None

                        body = json.loads(message.body.decode())

                        logger.info(f"body.keys(): {body.keys()}")

                        claim = body["claim"]

                        logger.info(f"claim: {claim}")

                        search_input = Claim(**claim)

                        logger.info(f"search_input: {search_input}")

                        # Process search request
                        result = await semantic_search_service.semantic_search(
                            search_input
                        )

                        response = result.model_dump()  # dict

                        # Compute metrics, insert metrics to database
                        metrics = compute_metrics(response)

                        # Log success to monitoring
                        await publish_monitoring_event.publish_event(
                            event_type="complete",
                            module_name="evidence_retrieval",
                            event_data=metrics,
                        )

                        logger.info(f"response: {response}")

                        await channel.default_exchange.publish(
                            Message(
                                body=json.dumps(response, cls=DateTimeEncoder).encode(),
                                correlation_id=message.correlation_id,
                                content_type="application/json",
                            ),
                            routing_key=message.reply_to,
                        )

                        logger.info("Request complete")

                except Exception as e:
                    # Log error to monitoring
                    await publish_monitoring_event.publish_event(
                        event_type="error",
                        module_name="evidence_retrieval",
                        event_data={
                            "claim_text": claim,
                            "status": "error",
                            "error": str(e),
                        },
                    )

                    logger.exception("Processing error for message %r", message)


if __name__ == "__main__":
    asyncio.run(main())
