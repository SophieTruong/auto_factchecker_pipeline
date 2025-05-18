import asyncio

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool

import os
import dotenv

from .app_logging import logger

dotenv.load_dotenv(dotenv.find_dotenv())

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

logger.info(f"RABBITMQ_URL: {RABBITMQ_URL}")

class RabbitMQConnectionPool:
    
    def __init__(self, url: str):
        
        self.url = url
        
        async def get_connection() -> AbstractRobustConnection:
            
            return await aio_pika.connect_robust(self.url)
        
        self.connection_pool: Pool = Pool(get_connection, max_size=2)
        
        self.channel_pool: Pool = Pool(self.get_channel, max_size=10)
        
    async def get_channel(self) -> aio_pika.Channel:
        
        async with self.connection_pool.acquire() as connection:
            
            return await connection.channel()
    
    async def close(self):
        
        await self.channel_pool.close()
        
        await self.connection_pool.close()
        
# Create a singleton instance
rabbitmq_pool = RabbitMQConnectionPool(RABBITMQ_URL)