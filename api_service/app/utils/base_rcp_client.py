from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage

import json

import uuid

import asyncio
from typing import MutableMapping

from .app_logging import logger

from .rabbitmq_connection_pool import rabbitmq_pool

from .uuid_encoder import UUIDEncoder

class BaseRpcClient:
        
    def __init__(self):
        
        self.futures: MutableMapping[str, asyncio.Future] = {}
    
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
        
    async def _rcp_call(self, message_data: dict, routing_key: str):

        correlation_id = str(uuid.uuid4())
        
        logger.info(f"A correlation_id is generated for _rcp_call: {correlation_id}")  
        
        loop = asyncio.get_running_loop()
        
        future = loop.create_future()
        
        self.futures[correlation_id] = future
            
        try:
            # Publish message
            async with rabbitmq_pool.channel_pool.acquire() as channel:
                
                await channel.set_qos(prefetch_count=10)
                
                # Declare 1 temporary queue: for response. Must be deleted after use
                callback_queue = await channel.declare_queue(
                    exclusive=True, 
                    auto_delete=True, 
                    durable=False
                )
                
                consumer_tag = await callback_queue.consume(self.on_response, no_ack=True)
                
                try:
                    message = Message(

                        body=json.dumps(message_data, cls=UUIDEncoder).encode(),

                        content_type='application/json',

                        correlation_id=correlation_id,

                        reply_to=callback_queue.name,
                    )

                    # DEFAULT EXCHANGE: publish message
                    await channel.default_exchange.publish(
                        
                        message,
                        
                        routing_key=routing_key,
                        
                    )
                    
                    logger.info(f"Published message to {routing_key}")
                    
                    # Wait for response
                    return await future
                
                finally:
                    
                    if consumer_tag:
                        
                        logger.info(f"Cancelling consumer_tag: {consumer_tag}")
                        
                        await callback_queue.cancel(consumer_tag)
                        
                    await callback_queue.delete()
        
        except Exception as e:
            
            self.futures.pop(correlation_id, None)
            
            logger.error(f"Error in _rcp_call: {e}")
            
            raise
