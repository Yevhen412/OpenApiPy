# ctrader_client.py

import asyncio
import websockets
import json

TOKEN = "ВСТАВЬ_СЮДА_ACCESS_TOKEN"

async def connect():
    uri = "wss://openapi.ctrader.com:5035"

    async with websockets.connect(uri) as websocket:
        # Отправка команды инициализации
        await websocket.send(json.dumps({
            "payloadType": "authorizeReq",
            "payload": {
                "accessToken": TOKEN
            }
        }))

        # Подписка на котировки по EURUSD
        await websocket.send(json.dumps({
            "payloadType": "subscribeForSpotsReq",
            "payload": {
                "cTraderAccountId": 1234567,  # ← заменишь на свой ID
                "symbolId": 1  # EURUSD
            }
        }))

        # Слушаем ответы
        while True:
            response = await websocket.recv()
            print(response)

# Запуск
if __name__ == "__main__":
    asyncio.run(connect())
