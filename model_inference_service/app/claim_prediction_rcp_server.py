import asyncio
import json

from aio_pika import Message, connect

from aio_pika.abc import AbstractIncomingMessage

import mlflow

from model import InferenceResult, ModelMetadata

from utils import load_yaml_file, parse_datetime, logger

# Read model environment variables
import dotenv

import os

dotenv.load_dotenv(dotenv.find_dotenv())

# Load model environment variables
MODEL_URI = os.getenv("MODEL_URI")

MODEL_METADATA = os.getenv("MODEL_METADATA")

logger.info(f"MODEL_URI: {MODEL_URI}")

logger.info(f"MODEL_METADATA: {MODEL_METADATA}")

# Load model
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

    try:
        
        # Perform connection

        connection = await connect(RABBITMQ_URL)

        # Creating a channel

        channel = await connection.channel()

        exchange = channel.default_exchange

        # Declaring queue

        queue = await channel.declare_queue(
            "rpc_claim_detection_queue",
            durable=True,  # Must match the durable=true in definitions.json
            auto_delete=False  # Must match auto_delete=false in definitions.json
        )


        logger.info(" [x] Awaiting RPC requests for claim detection")


        # Start listening the queue with name 'hello'

        async with queue.iterator() as qiterator:

            message: AbstractIncomingMessage

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
                            "inference_results": [InferenceResult(label=p).model_dump() for p in predictions]
                        }
                        
                        logger.info(f" [.] response_body: {response_body}")
                                            
                        # Convert dict to JSON string first, then encode
                        response_json = json.dumps(response_body)

                        logger.info(f" [.] response_json: {response_json}")
                        
                        await exchange.publish(

                            Message(

                                body=response_json.encode(),

                                correlation_id=message.correlation_id,

                            ),

                            routing_key=message.reply_to,

                        )

                        print("Request complete")

                except Exception:

                    logger.exception("Processing error for message %r", message)
    except Exception as e:
        
        logger.error(f"Error connecting to RabbitMQ: {e}")
        
        raise e

if __name__ == "__main__":

    asyncio.run(main())