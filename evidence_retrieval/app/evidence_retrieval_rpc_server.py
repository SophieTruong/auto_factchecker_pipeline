import json
from typing import List

import aio_pika
from aio_pika import Message, connect

from aio_pika.abc import AbstractIncomingMessage, AbstractChannel, AbstractConnection

import asyncio

from services import SemanticSearchService
from model import Claim
from app_logging import logger

import os
import dotenv

from datetime import datetime

# Import the DateTimeEncoder
from web_search_retrieval import DateTimeEncoder

dotenv.load_dotenv(dotenv.find_dotenv())

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

async def main():
    logger.info("Starting queue consumer")
            
    # 1. Initialize Semantic search service
    semantic_search_service = SemanticSearchService()
    
    logger.info("Initialized Semantic search service")
    
    # 2. Create connection to rabbitmq
    try:
        
        connection = await connect(RABBITMQ_URL)
        
        logger.info(f"Connected to RabbitMQ at {RABBITMQ_URL}")
        
        channel = await connection.channel()
        
        await channel.set_qos(prefetch_count=10)
        
        logger.info(f"Channel created")
        
        exchange = channel.default_exchange
        
        logger.info(f"Exchange created")

        queue = await channel.declare_queue(
            "rpc_evidence_retrieval_queue",
            durable=True,  # Must match the durable=true in definitions.json
            auto_delete=False  # Must match auto_delete=false in definitions.json
        )
        logger.info(f"Queue created: {queue.name}")
        
        logger.info(" [x] Awaiting RPC requests")

        async with queue.iterator() as qiterator:

            message: AbstractIncomingMessage

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
                        result = await semantic_search_service.semantic_search(search_input)
                        
                        response = result.model_dump()
                        
                        logger.info(f"response: {response}")

                        await exchange.publish(

                            Message(

                                body=json.dumps(response, cls=DateTimeEncoder).encode(), 

                                correlation_id=message.correlation_id,
                
                                content_type='application/json'

                            ),

                            routing_key=message.reply_to,

                        )

                        logger.info("Request complete")

                except Exception:

                    logger.exception("Processing error for message %r", message)

    except Exception as e:
        
        logger.error(f"Error connecting to RabbitMQ: {e}")
        
        raise e

if __name__ == "__main__":
    asyncio.run(main())