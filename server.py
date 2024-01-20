import asyncio
import argparse
import uuid
import ast
import random
import aioconsole
from enum import Enum

player_count = 0
max_players = 0
server_address = '0.0.0.0'
port = 0  

class GameStatus(Enum):
    waiting = 0
    playing = 1
    game_over = 2

class GameServer(asyncio.DatagramProtocol):
    # status = GameStatus.waiting
    uuid_set = set()
    uuid_map = {}
    
    def __init__(self):
        super().__init__()
        ...
        
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        # Print message
        # print(f"Received message '{message}' from {addr}")
        
        # Echo message
        # self.transport.sendto(message.encode(), addr)
        raw_message = message
        message = ast.literal_eval(message)
        
            
        if message["action"] == "status":
            # send status to all players other than the sender
            for uuid, addr in self.uuid_map.items():
                if uuid != message["uuid"]:
                    self.send_message(raw_message, addr)
                    
        elif message["action"] == "join":
            if message["uuid"] not in self.uuid_set:
                self.send_status({"action": "join", "status": "failed"}, addr)
                return
                
            self.uuid_map[message["uuid"]] = addr
            print(f"{message['uuid']} has joined the game!")
            self.send_status({"action": "join", "status": "success"}, addr)

    def send_message(self, message, addr):
        self.transport.sendto(message.encode(), addr)
        
    def send_status(self, status, addr):
        self.transport.sendto(str(status).encode(), addr)

    @staticmethod
    async def create_udp_server():
        global server_address, port
        while True:
            try:
                # with random port over 1024
                port = random.randint(1024, 65535)
                transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
                    GameServer,
                    local_addr=(server_address, port)
                )
                break
            except OSError as e:
                print(f"Port {port} is already in use. Trying another port...")

        print(f"UDP server listening on {server_address}:{port}")
        
        return transport

        # try:
        #     # 保持伺服器運行
        #     await asyncio.Future()
        # finally:
        #     # 關閉伺服器
        #     transport.close()

async def lobby_handler(reader, writer, start_event):
    global player_count, max_players
    data = (await reader.read(255)).decode()

    data = ast.literal_eval(data)
    if data["action"] == "handshake":

        if player_count < max_players:
            print(f"Player {player_count} joined!")
            player_count += 1
            created_uuid = str(uuid.uuid1())
            GameServer.uuid_set.add(created_uuid)
            message = {"action": "handshake", "uuid": created_uuid}
        else:
            message = {"action": "handshake", "uuid": None}
        
        writer.write(str(message).encode())
        await writer.drain()

        received = await reader.read(255)
        received = received.decode()

        await start_event.wait()

        # 在這裡加入相應的邏輯，例如向客戶端發送訊息
        wait_message = {"action": "start_game", "port": port, "uuids": list(GameServer.uuid_set), "player_count": player_count}
        writer.write(str(wait_message).encode())
        await writer.drain()

async def read_keyboard_input(start_event):
    while True:
        data = (await aioconsole.ainput()).strip().lower()
        if data == "start":
            start_event.set()
            break

async def run_server():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-players', type=int, default=4)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=12345)

    args = parser.parse_args()

    global max_players
    max_players = args.max_players

    print(f"Starting server on {args.host}:{args.port}...")
    print('Enter "start" to start the game: ')

    start_event = asyncio.Event()

    udp_server = await GameServer.create_udp_server()

    lobby_task = asyncio.create_task(asyncio.start_server(lambda r, w: lobby_handler(r, w, start_event),
                                                           args.host,
                                                           args.port))

    keyboard_task = asyncio.create_task(read_keyboard_input(start_event))

    await start_event.wait()
    lobby_task.cancel()
    keyboard_task.cancel()

    return udp_server

async def main():
    udp_server = await run_server()
    
    try:
        # 保持伺服器運行
        await asyncio.Future()
    finally:
        # 關閉伺服器
        udp_server.close()

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
