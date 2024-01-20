import asyncio
import ast

class GameClient(asyncio.DatagramProtocol):
    def __init__(self, uuid):
        super().__init__() 
        self.transport = None
        self.uuid = uuid
        self.datagram_received_cb = None
              
    def connection_made(self, transport):
        self.transport = transport
        self.send_status({'action': 'join'})

    def datagram_received(self, data, addr):
        message = data.decode()
        self.datagram_received_cb(message)
        # print(f"Received message '{message}' from {addr}")
        
    def send_message(self, message):
        self.transport.sendto(message.encode())
        
    def send_status(self, status):
        if 'action' not in status:
            status['action'] = 'status'
        status['uuid'] = self.uuid
        self.transport.sendto(str(status).encode())
        
    def error_received(self, exc):
        ...
    
    def connection_lost(self, exc):
        ...
    
    @staticmethod
    async def create_udp_client(uuid, server_address, port):
        _, protocol = await asyncio.get_event_loop().create_datagram_endpoint(lambda: GameClient(uuid),
                                                                            remote_addr=(server_address, port))
        return protocol

    @staticmethod
    async def join_game(server_address, port):
        reader, writer = await asyncio.open_connection(server_address, port)

        print("Joining....")
        
        message = {"action": "handshake"}
        writer.write(str(message).encode())
        await writer.drain()
        received = await reader.read(255)
        received = received.decode()
        # print(f'Received: {received}')
        received = ast.literal_eval(received)
        assert received["action"] == "handshake"
        uuid = received["uuid"]
        assert uuid is not None
        print(f"UUID: {uuid}")
        
        message = {"action": "wait"}
        writer.write(str(message).encode())
        await writer.drain()
        received = await reader.read(255)
        received = received.decode()
        received = ast.literal_eval(received)
        # print(f'Received: {received}')
        assert received["action"] == "start_game"
        gs_port = int(received["port"])
        player_count = int(received["player_count"])
        uuids = received["uuids"]

        writer.close()
        await writer.wait_closed()
        
        transport = await GameClient.create_udp_client(uuid, server_address, gs_port)
        
        return {'transport': transport, 'player_count': player_count, 'uuids': uuids}

async def main():  
    server_address = '127.0.0.1'
    port = 12345
    
    transport = await GameClient.join_game(server_address, port)
    
    transport.send_status({'message': 'hello'})
    
    # 保持伺服器運行
    try:
        await asyncio.Future()
    finally:
        ...
        
    # 關閉伺服器
    transport.close()

if __name__ == "__main__":
    asyncio.run(main(), debug=True)