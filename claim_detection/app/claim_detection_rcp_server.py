import asyncio
import json

from aio_pika import Message

from database.postgres import engine, Base, get_db

from services.claim_detection import ClaimDetectionService

from utils.uuid_encoder import UUIDEncoder

from utils.rabbitmq_connection_pool import rabbitmq_pool

from services.claim_annotation import ClaimAnnotationService

# TODO: Create pydantic model for the message
from models.source_document import SourceDocumentCreate

from models.claim import Claim

from models.claim_annotation_input import BatchClaimAnnotationInput

from models.claim_annotation import ClaimAnnotation

from utils.app_logging import logger

import os

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

logger.info("Claim prediction RCP server started")

# Load RabbitMQ environment variables
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")
RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/{RABBITMQ_VHOST}"
)


logger.info(f"RABBITMQ_URL: {RABBITMQ_URL}")

# Set up claim database:
Base.metadata.create_all(bind=engine)


async def handle_claim_request(message_body_dict: dict, db):
    """Handle different types of claim requests with a DB session"""

    request_type = message_body_dict["request_type"]

    data = message_body_dict["data"]

    # Initialize services with the current db session
    claim_detection_service = ClaimDetectionService(db=db)

    claim_annotation_service = ClaimAnnotationService(db=db)

    try:

        if request_type == "claim_detection_insert":

            logger.info(f" [.] claim_detection_insert data: {data}")

            # Handle insert
            source_document = SourceDocumentCreate(**data)

            claim_predictions = await claim_detection_service.get_predictions(
                source_document
            )

            return {"status": "success", "data": claim_predictions}

        elif request_type == "claim_detection_update":

            logger.info(f" [.] claim_detection_update data: {data}")

            # Handle update

            claims = [Claim(**claim) for claim in data]

            claims_updates = await claim_detection_service.update_claims(claims)

            return {"status": "success", "data": claims_updates}

        elif request_type == "claim_detection_get":

            logger.info(f" [.] claim_detection_get data: {data}")

            # Handle get
            claims = await claim_detection_service.get_claims(
                data["start_date"], data["end_date"]
            )

            return {"status": "success", "data": claims}

        elif request_type == "claim_annotation_insert":

            logger.info(f" [.] claim_annotation_insert data: {data}")

            # Handle annotation insert and publish monitoring event
            claim_annotations = await claim_annotation_service.create_claim_annotation(
                BatchClaimAnnotationInput(**data)
            )

            return {"status": "success", "data": claim_annotations}

        elif request_type == "claim_annotation_update":  # this might not be needed

            logger.info(f" [.] claim_annotation_update data: {data}")

            claim_annotations = [
                ClaimAnnotation(**claim_annotation) for claim_annotation in data
            ]

            # Handle annotation update
            updated_claim_annotations = (
                await claim_annotation_service.update_claim_annotation(
                    claim_annotations
                )
            )

            return {"status": "success", "data": updated_claim_annotations}

        else:
            raise ValueError(f"Invalid request type: {request_type}")

    except Exception as e:

        logger.exception(f"Error handling claim request: {e}")

        raise Exception(f"{e}")


def serialize_response_data(data):

    if data is None:

        return None

    elif isinstance(data, list):

        return [item.model_dump() for item in data]

    else:

        return data.model_dump()


async def main() -> None:

    # Wrap a connection pool around the consumer code: 1 connection
    async with rabbitmq_pool.channel_pool.acquire() as channel:

        await channel.set_qos(10)

        # Declaring 1 custom queue: Handle all requests for claim db
        # Persistent queue: No auto_delete
        queue = await channel.declare_queue(
            "rpc_claim_db_queue",  # MUST MATCH ROUTING KEY IN RCP CLIENT
            durable=True,
            auto_delete=False,
        )

        logger.info(" [x] Awaiting RPC requests for claim db")

        # Iterate over the queue: Handle all requests for claim db
        async with queue.iterator() as qiterator:

            async for message in qiterator:

                try:

                    async with message.process(requeue=False):

                        # If message don't have name of callback queue, RCP fails
                        assert message.reply_to is not None

                        message_body = message.body.decode()

                        logger.info(
                            f" [.] Claim detection RCP server: message_body received and decoded"
                        )

                        message_body_dict = json.loads(message_body)

                        with get_db() as db:

                            response_body = await handle_claim_request(
                                message_body_dict, db=db
                            )

                            response_body_data = serialize_response_data(
                                response_body["data"]
                            )

                            logger.info(
                                f" [.] response_body_data: {response_body_data}"
                            )

                            # Publish RCP response to the callback queue
                            await channel.default_exchange.publish(
                                Message(
                                    body=json.dumps(
                                        response_body_data, cls=UUIDEncoder
                                    ).encode("utf-8"),
                                    content_type="application/json",
                                    correlation_id=message.correlation_id,
                                ),
                                routing_key=message.reply_to,
                            )

                            logger.info("Request complete")

                except Exception as e:

                    logger.exception("Processing error for message %r", message)

                    await channel.default_exchange.publish(
                        Message(
                            body=json.dumps(
                                {"status": "error", "message": str(e)}, cls=UUIDEncoder
                            ).encode("utf-8"),
                            content_type="application/json",
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                    )


if __name__ == "__main__":
    asyncio.run(main())
