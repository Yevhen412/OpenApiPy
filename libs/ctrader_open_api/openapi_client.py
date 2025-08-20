# libs/ctrader_open_api/openapi_client.py
import asyncio
from loguru import logger
from ctrader_open_api.protobuf import spotware_pb2 as pb
from ctrader_open_api import Endpoints  # эти классы переиспользуем

class Client:
    def __init__(self, client_id, client_secret, environment=Endpoints.DEMO):
        from ctrader_open_api import Client as InnerClient
        self._inner = InnerClient(client_id=client_id, client_secret=client_secret, environment=environment)

    async def connect(self):
        await self._inner.connect()

    async def authenticate(self):
        await self._inner.authenticate()

    async def subscribe_for_account(self, account_id):
        await self._inner.subscribe_for_account(account_id)

    async def get_symbol_by_name(self, account_id, symbol):
        return await self._inner.get_symbol_by_name(account_id, symbol)

    async def subscribe_spot_symbol(self, account_id, symbol_ids):
        await self._inner.subscribe_spot_symbol(account_id, symbol_ids)

    async def listen(self):
        async for msg in self._inner.listen():
            yield msg
