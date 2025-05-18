from typing import List

from aio_pika import Message

from aio_pika.abc import AbstractIncomingMessage

import json

import uuid

import asyncio

from typing import MutableMapping

from utils.app_logging import logger

from utils.rabbitmq_connection_pool import rabbitmq_pool

import os

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

class ClaimPredictionRcpClient:    
    
    def __init__(self):
        
        self.futures: MutableMapping[str, asyncio.Future] = {}
    
    async def on_response(self, message: AbstractIncomingMessage):
        
        if message.correlation_id is None:
            
            logger.error(f"Bad message {message!r}")
            
            return

        try:
            future: asyncio.Future = self.futures.pop(message.correlation_id)
            
            future.set_result(message.body)
        
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            
            logger.warning(f"Received response for unknown correlation_id: {message.correlation_id}")
            
            return

        except Exception as e:

            logger.error(f"Error processing response: {e}")

            return
        
    async def get_model_predictions(self, claim_list: List[str]):
                
        correlation_id = str(uuid.uuid4())
        
        logger.info(f"A correlation_id is generated for get_model_predictions: {correlation_id}")  
        
        loop = asyncio.get_running_loop()

        future = loop.create_future()

        self.futures[correlation_id] = future
            
        try:

            # Publish message
            async with rabbitmq_pool.channel_pool.acquire() as channel:
                
                await channel.set_qos(prefetch_count=10)
                
                # Declare 1 temporary queue: for response. Must be deleted after use
                callback_queue = await channel.declare_queue(exclusive=True, auto_delete=True, durable=False)
                
                consumer_tag = await callback_queue.consume(self.on_response, no_ack=True)
                
                try:
                    message = Message(
                        
                        body=json.dumps({
                        
                            'claim': claim_list,
                        
                        }).encode(),
                        
                        content_type='application/json', # describe the mime-type of the encoding
                        
                        correlation_id=correlation_id, # correlate RPC responses with requests
                        
                        reply_to=callback_queue.name, # automatically generated queue name for response from RPC server
                    
                    )
                
                    await channel.default_exchange.publish(
                        message,
                        routing_key="rpc_claim_prediction_queue"
                    )
                        
                    logger.info(f"Published message")
                
                    return await future
                
                finally:
                    
                    if consumer_tag:
                    
                        logger.info(f"Cancelling consumer_tag: {consumer_tag}")
                    
                        await callback_queue.cancel(consumer_tag)
                    
                    await callback_queue.delete()

        except Exception as e:
            
            self.futures.pop(correlation_id, None)
            
            logger.error(f"Error in get_model_predictions: {e}")
            
            raise