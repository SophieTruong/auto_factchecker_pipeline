from utils.base_rcp_client import BaseRpcClient

from models.semantic_search_input import SemanticSearchInput
import asyncio
from typing import MutableMapping

from utils.app_logging import logger

import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")
RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/{RABBITMQ_VHOST}"
)


class EvidenceRetrievalRpcClient(BaseRpcClient):

    async def get_search_result(self, claim: SemanticSearchInput):

        message_data = {
            "claim": claim.model_dump(),
        }

        return await self._rcp_call(message_data, "rpc_evidence_retrieval_queue")
