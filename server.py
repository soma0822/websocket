# websocket_server_with_rooms.py

import asyncio
import websockets
import aioconsole
from collections import defaultdict

# 各ルームのクライアントを管理
rooms = defaultdict(set)

async def handler(websocket, path):
    room_id = await assign_to_room(websocket)
    print(f"Client connected to room {room_id}")
    try:
        await receive_message(websocket, room_id)
    finally:
        # クライアントが切断されたら、ルームから削除
        rooms[room_id].remove(websocket)
        if not rooms[room_id]:  # ルームが空になったら削除
            del rooms[room_id]

async def assign_to_room(websocket):
    # 最大2クライアントまでのルームに参加させる
    for room_id, clients in rooms.items():
        if len(clients) < 2:
            clients.add(websocket)
            return room_id
    # 新しいルームを作成して参加
    new_room_id = len(rooms) + 1
    rooms[new_room_id].add(websocket)
    return new_room_id

async def receive_message(websocket, room_id):
    # クライアントからのメッセージを受信し、ルーム内にブロードキャスト
    async for message in websocket:
        print(f"Client in room {room_id}: {message}")
        await broadcast_to_room(room_id, f"Client says: {message}", websocket)

async def broadcast_to_room(room_id, message, sender=None):
    # 指定したルーム内のクライアントにメッセージを送信
    for client in rooms[room_id]:
        if client != sender:  # 送信者には送らない
            await client.send(message)

async def server_input():
    # メインの入力処理を1つだけ作成し、全ルームにブロードキャスト
    while True:
        message = await aioconsole.ainput("Server: ")
        # 各ルームにメッセージを送信
        for room_id in rooms:
            await broadcast_to_room(room_id, f"Server says: {message}")

async def main():
    # サーバー起動とメイン入力処理の同時実行
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket server with rooms started on ws://localhost:8765")
    await asyncio.gather(server.wait_closed(), server_input())

asyncio.run(main())
