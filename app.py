import os
import asyncio
from fastapi import FastAPI
from loguru import logger

# cTrader Open API (из OpenApiPy)
from ctrader_open_api import Client, Endpoints, Protobuf
from ctrader_open_api.protobuf import spotware_pb2 as pb

app = FastAPI()

CLIENT_ID = os.getenv("CTRADER_CLIENT_ID")
CLIENT_SECRET = os.getenv("CTRADER_CLIENT_SECRET")
ACCOUNT_ID = int(os.getenv("CTRADER_ACCOUNT_ID", "0"))
SYMBOL = os.getenv("SYMBOL", "EURUSD")

@app.get("/")
def ping():
    return {"ok": True, "msg": "Service up", "symbol": SYMBOL}

@app.on_event("startup")
async def _startup():
    # запускаем «демона», который будет лить котировки в лог Railway
    asyncio.create_task(stream_quotes())

async def stream_quotes():
    try:
        client = Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            environment=Endpoints.DEMO,   # именно DEMO для IC Markets демо-счёта
        )
        await client.connect()
        logger.info("Connected to cTrader Open API (DEMO)")

        # При первом запуске в LOGS появится OAuth-ссылка — открой её и подтверди доступ
        await client.authenticate()
        logger.info("Authenticated")

        # Привязать аккаунт
        await client.subscribe_for_account(ACCOUNT_ID)
        logger.info(f"Subscribed to account {ACCOUNT_ID}")

        # Получить symbol_id и подписаться на тики
        sym = await client.get_symbol_by_name(ACCOUNT_ID, SYMBOL)
        sid = sym.symbol.symbol_id
        await client.subscribe_spot_symbol(ACCOUNT_ID, [sid])
        logger.info(f"Subscribed to ticks: {SYMBOL} (symbol_id={sid})")

        async for msg in client.listen():
            if isinstance(msg.payload, pb.SymbolTickEvent):
                for t in msg.payload.ticks:
                    if t.symbol_id == sid:
                        bid = t.bid / 10**5
                        ask = t.ask / 10**5
                        mid = (bid + ask) / 2
                        logger.info(f"{SYMBOL} bid={bid:.5f} ask={ask:.5f} mid={mid:.5f}")

    except Exception as e:
        logger.exception(f"Quotes stream crashed: {e}")
