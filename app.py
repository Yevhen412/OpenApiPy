import sys
import os
import asyncio
import uvicorn
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# Добавляем путь до библиотек
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

from ctrader_open_api.openapi_client import Client, Endpoints

# Логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI-приложение
app = FastAPI()

# Получаем переменные окружения
CLIENT_ID = os.getenv("CTRADER_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CTRADER_CLIENT_SECRET", "")
ACCOUNT_ID = int(os.getenv("CTRADER_ACCOUNT_ID", "0"))
SYMBOL = os.getenv("SYMBOL", "EURUSD")

_stream_task = None

# Тестовый маршрут
@app.get("/")
def root():
    return {"ok": True, "symbol": SYMBOL}


# Колбэк после авторизации
@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("<h2>Error: No code found in callback</h2>", status_code=400)
    return HTMLResponse(f"<h2>Authorization code:</h2><p>{code}</p>")


# Запускаем поток котировок после старта
@app.on_event("startup")
async def on_startup():
    global _stream_task
    _stream_task = asyncio.create_task(stream_quotes())


async def stream_quotes():
    if not CLIENT_ID or not CLIENT_SECRET or not ACCOUNT_ID:
        logger.error("Missing required environment variables.")
        return

    client = Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, environment=Endpoints.DEMO)
    await client.connect()
    logger.info("Connected to cTrader")

    await client.authenticate()
    logger.info("Authenticated with cTrader")

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


# Точка входа при запуске напрямую (не обязательна на Railway)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
