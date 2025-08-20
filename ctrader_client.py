# ctrader_client.py

import asyncio
import websockets
import json
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCOUNT_ID = os.getenv("CTRADER_ACCOUNT_ID")  # ← тоже вынесем в переменные

async def connect():
    uri = "wss://openapi.ctrader.com:5035"

    async with websockets.connect(uri) as websocket:
        # Авторизация
        await websocket.send(json.dumps({
            "payloadType": "authorizeReq",
            "payload": {
                "accessToken": ACCESS_TOKEN
            }
        }))

        # Подписка на EURUSD (symbolId = 1)
        await websocket.send(json.dumps({
            "payloadType": "subscribeForSpotsReq",
            "payload": {
                "cTraderAccountId": int(ACCOUNT_ID),
                "symbolId": 1
            }
        }))

        # Слушаем входящие данные
        while True:
            response = await websocket.recv()
            print(response)

if __name__ == "__main__":
    asyncio.run(connect())
