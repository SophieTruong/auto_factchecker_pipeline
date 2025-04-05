import asyncio

import json

import aio_pika

from aio_pika import Message, connect_robust

from aio_pika.abc import AbstractRobustConnection, AbstractIncomingMessage

from aio_pika.pool import Pool

import mlflow

from model import InferenceResult, ModelMetadata

from utils import load_yaml_file, parse_datetime, logger, UUIDEncoder

# Read model environment variables
import dotenv

import os

dotenv.load_dotenv(dotenv.find_dotenv())

# Load SetFit model environment variables
MODEL_URI = os.getenv("MODEL_URI")

MODEL_METADATA = os.getenv("MODEL_METADATA")

logger.info(f"MODEL_URI: {MODEL_URI}")

logger.info(f"MODEL_METADATA: {MODEL_METADATA}")

# Load SetFit model
model = mlflow.pyfunc.load_model(MODEL_URI)

model_metadata = load_yaml_file(MODEL_METADATA)

model_metadata = ModelMetadata(
    model_name=model_metadata["name"],
    model_version=str(model_metadata["version"]),
    model_path=model_metadata["source"],
    created_at=parse_datetime(model_metadata["creation_timestamp"])
)

logger.info(f"Model metadata: {model_metadata}")

# Load RabbitMQ environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

logger.info(f"RABBITMQ_URL: {RABBITMQ_URL}")

async def main() -> None:
    
    # 1. Create connection pool: 1 connection
    async def get_connection() -> AbstractRobustConnection:
        return await aio_pika.connect_robust(RABBITMQ_URL)

    connection_pool: Pool = Pool(get_connection, max_size=2)

    async def get_channel() -> aio_pika.Channel:
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool: Pool = Pool(get_channel, max_size=10)

    queue_name = "rpc_claim_prediction_queue"
    
    async with channel_pool.acquire() as channel:  # type: aio_pika.Channel
            
        await channel.set_qos(10)

        queue = await channel.declare_queue(
            queue_name, 
            durable=True, 
            auto_delete=False
        )

        logger.info(" [x] Awaiting RPC requests for claim prediction client")
            
        # Start listening the queue rpc_claim_prediction_queue

        async with queue.iterator() as qiterator:

            async for message in qiterator:

                try:

                    async with message.process(requeue=False):

                        assert message.reply_to is not None

                        message_body = message.body.decode() #List[str]

                        logger.info(f" [.] message_body: {message_body}")
                        
                        message_body_dict = json.loads(message_body)
                            
                        claim_list = message_body_dict["claim"]

                        logger.info(f" [.] claim_list: {claim_list}")
                        
                        predictions = await asyncio.to_thread(model.predict, claim_list)
                        
                        predictions = predictions.cpu().numpy().tolist()

                        logger.info(f" [.] predictions: {predictions}")
                        
                        response_body = {
                            "model_metadata": model_metadata.model_dump(),
                            "inference_results": [
                                InferenceResult(label=p).model_dump() 
                                for p in predictions
                            ]
                        }
                        
                        logger.info(f" [.] response_body: {response_body}")
                                            
                        await channel.default_exchange.publish(

                            Message(

                                body=json.dumps(response_body, cls=UUIDEncoder).encode('utf-8'),

                                correlation_id=message.correlation_id,

                            ),

                            routing_key=message.reply_to,

                        )

                        logger.info("Request complete")

                except Exception:

                    logger.exception("Processing error for message %r", message)

if __name__ == "__main__":

    asyncio.run(main())