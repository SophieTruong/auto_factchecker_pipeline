from aio_pika import Message, ExchangeType, DeliveryMode

from datetime import datetime 

import json

from utils.rabbitmq_connection_pool import rabbitmq_pool

from utils.uuid_encoder import UUIDEncoder

from utils.app_logging import logger

class PublishMonitoringEvent:
    
    def __init__(self):
        
        self.exchange_name = "model_monitoring_exchange"
        
    async def publish_event(self, event_type: str, module_name: str, event_data: dict):
        
        # Reuse connection pool
        async with rabbitmq_pool.channel_pool.acquire() as channel:
            
            # CUSTOM EXCHANGE: for publish logging events
            topic_logs_exchange = await channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC
            )
            
            routing_key = f"monitoring.{event_type}.{module_name}"
            
            message_body = {
                "timestamp": datetime.now(),
                "event_type": event_type,
                "module_name": module_name,
                "data": event_data
            }
            
            message = Message(
                json.dumps(message_body, cls=UUIDEncoder).encode("utf-8"),
                delivery_mode=DeliveryMode.PERSISTENT
            )
            
            await topic_logs_exchange.publish(message, routing_key=routing_key)

            logger.info(f" [x] Sent monitoring event: {routing_key}")
            