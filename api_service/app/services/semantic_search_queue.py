from aio_pika import connect, Message, ExchangeType
from aio_pika.abc import (
    AbstractChannel, 
    AbstractConnection, 
    AbstractIncomingMessage, 
    AbstractQueue,
)
import json
import uuid
from models.semantic_search_input import SemanticSearchInputs
import asyncio
from typing import MutableMapping

from utils.app_logging import logger

import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")


class SemanticSearchQueueService:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    
    def __init__(self):
        self.futures: MutableMapping[str, asyncio.Future] = {}

    async def connect(self):
        self.connection = await connect(RABBITMQ_URL)
        
        logger.info(f"Connected to RabbitMQ at {RABBITMQ_URL}")
    
        self.channel = await self.connection.channel()
        
        await self.channel.set_qos(prefetch_count=10)
        
        logger.info(f"Channel created")

        self.callback_queue = await self.channel.declare_queue(exclusive=True)

        await self.callback_queue.consume(self.on_response, no_ack=True)
        
        logger.info(f"Callback queue created")

        return self
    
    async def on_response(self, message: AbstractIncomingMessage):
        if message.correlation_id is None:
            
            logger.info(f"Bad message {message!r}")
            
            return

        try:
            future: asyncio.Future = self.futures.pop(message.correlation_id)
            
            future.set_result(message.body)
        
        except KeyError as e:
            logger.info(f"KeyError: {e}")
            
            logger.warning(f"Received response for unknown correlation_id: {message.correlation_id}")
            
            return

        except Exception as e:

            logger.error(f"Error processing response: {e}")

            return
        
    async def get_search_result(self, claims: SemanticSearchInputs):
                
        correlation_id = str(uuid.uuid4())
        
        logger.info(f"A correlation_id is generated for get_search_result: {correlation_id}")  
        
        loop = asyncio.get_running_loop()

        future = loop.create_future()

        self.futures[correlation_id] = future
        
        # Publish message
        message = Message(
                body=json.dumps({
                    'claims': claims.model_dump(),
                    'correlation_id': correlation_id
                }).encode(),
                content_type='application/json', # describe the mime-type of the encoding
                correlation_id=correlation_id, # correlate RPC responses with requests
                reply_to=self.callback_queue.name, # automatically generated queue name for response from RPC server
            )
        
        await self.channel.default_exchange.publish(
            message,
            routing_key="rpc_queue"
        )
        
        logger.info(f"Published message")
        
        return await future
