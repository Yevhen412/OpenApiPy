import os
import asyncio
from fastapi import FastAPI, Request
from loguru import logger

# SDK от Spotware (Python)
from openapipy import Client, Endpoints, Protobuf
from ctrader_open_api.protobuf import spotware_pb2 as pb

app = FastAPI(title="ICM Quotes (cTrader Open API)")

CLIENT_ID = os.getenv("CTRADER_CLIENT_ID")
CLIENT_SECRET = os.getenv("CTRADER_CLIENT_SECRET")
ACCOUNT_ID = int(os.getenv("CTRADER_ACCOUNT_ID", "0"))
SYMBOL = os.getenv("SYMBOL", "EURUSD")

_stream_task: asyncio.Task | None = None

@app.get("/")
def root():
    return {
        "ok": True,
        "msg": "Service up",
        "symbol": SYMBOL,
        "account_id": ACCOUNT_ID
    }

@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    # На всякий случай — чтобы видеть, что пришло от OAuth (обычно SDK справляется сам)
    params = dict(request.query_params)
    logger.info(f"OAuth callback params: {params}")
    return {"ok": True, "received": params}

@app.post("/start")
async def start_stream():
    global _stream_task
    if _stream_task and not _stream_task.done():
        return {"ok": True, "status": "already running"}
    _stream_task = asyncio.create_task(stream_quotes())
    return {"ok": True, "status": "started"}

@app.post("/stop")
async def stop_stream():
    global _stream_task
    if _stream_task and not _stream_task.done():
        _stream_task.cancel()
        try:
            await _stream_task
        except asyncio.CancelledError:
            pass
    _stream_task = None
    return {"ok": True, "status": "stopped"}

@app.on_event("startup")
async def on_startup():
    # можно автоматически стартовать; если хочешь вручную — закомментируй строку ниже
    asyncio.create_task(stream_quotes())

async def stream_quotes():
    try:
        if not CLIENT_ID or not CLIENT_SECRET or not ACCOUNT_ID:
            raise RuntimeError("Env vars missing: CTRADER_CLIENT_ID / CTRADER_CLIENT_SECRET / CTRADER_ACCOUNT_ID")

        client = Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            environment=Endpoints.DEMO   # демо-среда
        )

        await client.connect()
        logger.info("✅ Connected to cTrader Open API (DEMO)")

        # При первом запуске SDK выведет в логи ссылку — открой её и подтверди доступ
        await client.authenticate()
        logger.info("🔑 Authenticated")

        await client.subscribe_for_account(ACCOUNT_ID)
        logger.info(f"📥 Subscribed to account {ACCOUNT_ID}")

        sym = await client.get_symbol_by_name(ACCOUNT_ID, SYMBOL)
        symbol_id = sym.symbol.symbol_id
        await client.subscribe_spot_symbol(ACCOUNT_ID, [symbol_id])
        logger.info(f"📡 Subscribed to ticks: {SYMBOL} (symbol_id={symbol_id})")

        async for msg in client.listen():
            if isinstance(msg.payload, pb.SymbolTickEvent):
                for t in msg.payload.ticks:
                    if t.symbol_id == symbol_id:
                        bid = t.bid / 10**5
                        ask = t.ask / 10**5
                        mid = (bid + ask) / 2
                        logger.info(f"💹 {SYMBOL} bid={bid:.5f} ask={ask:.5f} mid={mid:.5f}")

    except Exception as e:
        logger.exception(f"Quotes stream crashed: {e}")
