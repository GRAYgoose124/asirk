import asyncio


class IrcServerProtocol(asyncio.Protocol):
    clients = {}  # Class variable to track all clients
    ping_interval = 10

    def __init__(self):
        self.transport = None
        self.nickname = None

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info("peername")
        print(f"Connection from {peername}")
        IrcServerProtocol.clients[self] = asyncio.get_event_loop().time()

    def data_received(self, data):
        messages = data.decode().split("\r\n")
        for message in messages:
            if message:  # Ignore empty messages
                print(f"Data received: {message}")
                self.process_message(message)

    def connection_lost(self, exc):
        print("The client closed the connection")
        self.transport.close()
        del IrcServerProtocol.clients[self]

    def process_message(self, message):
        if message.startswith("NICK"):
            self.nickname = message.split(" ")[1]
            print(f"Nickname set to {self.nickname}")
        elif message.startswith("USER"):
            # Handle user registration here
            pass
        elif message.startswith("PRIVMSG"):
            # Handle private messages here
            pass
        elif message.startswith("PONG"):
            IrcServerProtocol.clients[self] = asyncio.get_event_loop().time()
        elif message.startswith("JOIN"):
            channel = message.split(" ")[1]
            self.channels.add(channel)
            print(f"{self.nickname} joined {channel}")
            # Handle channel joining logic here
        # Add more command handling as needed

    def start_ping(self):
        self.last_pong = asyncio.get_event_loop().time()
        asyncio.get_event_loop().create_task(self.ping_client())

    @classmethod
    async def check_clients(cls):
        while True:
            await asyncio.sleep(cls.ping_interval)
            current_time = asyncio.get_event_loop().time()
            for client in list(cls.clients.keys()):
                if current_time - cls.clients[client] > cls.ping_interval:
                    print("Client did not respond to PING, closing connection.")
                    client.transport.close()
                else:
                    print(f"Pinging {client.nickname}")
                    client.transport.write(b"PING :ping\n")


async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(lambda: IrcServerProtocol(), "127.0.0.1", 6667)

    async with server:
        loop.create_task(IrcServerProtocol.check_clients())
        await server.serve_forever()


asyncio.run(main())
