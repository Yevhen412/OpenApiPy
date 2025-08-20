import sys
import os
import asyncio 
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

from ctrader_open_api.openapi_client import Client
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "OK"}

CLIENT_ID = os.getenv("CTRADER_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CTRADER_CLIENT_SECRET", "")
ACCOUNT_ID = int(os.getenv("CTRADER_ACCOUNT_ID", "0"))
SYMBOL = os.getenv("SYMBOL", "EURUSD")

_stream_task = None

@app.get("/")
def root():
    return {"ok": True, "symbol": SYMBOL}

@app.on_event("startup")
async def on_startup():
    global _stream_task
    _stream_task = asyncio.create_task(stream_quotes())

async def stream_quotes():
    if not CLIENT_ID or not CLIENT_SECRET or not ACCOUNT_ID:
        logger.error("Missing env vars")
        return

    client = Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, environment=Endpoints.DEMO)
    await client.connect()
    logger.info("Connected")

    await client.authenticate()
    logger.info("Authenticated")

    await client.subscribe_for_account(ACCOUNT_ID)
    sym = await client.get_symbol_by_name(ACCOUNT_ID, SYMBOL)
    symbol_id = sym.symbol.symbol_id
    await client.subscribe_spot_symbol(ACCOUNT_ID, [symbol_id])
    logger.info(f"Subscribed to {SYMBOL}")

    async for msg in client.listen():
        if hasattr(msg.payload, "ticks"):
            for t in msg.payload.ticks:
                if t.symbol_id == symbol_id:
                    bid = t.bid / 10**5
                    ask = t.ask / 10**5
                    mid = (bid + ask) / 2
                    logger.info(f"{SYMBOL} bid={bid:.5f} ask={ask:.5f} mid={mid:.5f}")
