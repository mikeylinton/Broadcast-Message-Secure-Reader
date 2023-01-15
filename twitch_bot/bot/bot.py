from twitch_bot.twitch.twitch_irc_client import get_twitch_irc_client
from twitch_bot.obs.obs_client import get_obs_client
from twitch_bot.data.consts import KEYRING_SERVICE
from twitch_bot.data.logger import logger
import websockets
import asyncio
import keyring

class Bot:
    def __init__(self):
        self.connections = set()
        self.twitch = None
        self.obs = None

    async def stop(self):
        if self.twitch.ws:
            await self.twitch.disconnect()
        if self.obs.ws:
            await self.obs.disconnect()

    # async def handle_request(self, client, request):
    #     await client.actions["sceneItemTransform"](**request["data"])

    async def handle_socket(self, client):
        async with websockets.connect(client.uri) as ws:
            try:
                client.ws = ws
                if client.__class__ == self.twitch.__class__:
                    await client.send_command(f"PASS {client.oauth_token}")
                    await client.send_command(f"NICK {client.username}")
                    await client.send_command("CAP REQ :twitch.tv/commands twitch.tv/tags")
                    for channel in client.channels:
                        await client.send_command(f"JOIN #{channel}")
                async for received_msgs in ws:
                    for received_msg in received_msgs.split("\r\n"):
                        if len(received_msg) == 0:
                            continue
                        request = await client.handle_message(received_msg)
                        if request:
                            logger.info(f"request recieved: {request}")
            except asyncio.CancelledError:
                 await self.stop()

    async def handler(self):
        try:
            await asyncio.wait([self.handle_socket(client) for client in self.connections])
        except asyncio.CancelledError:
                pass

    def reset(self):
        try:
            keyring.delete_password(KEYRING_SERVICE,"twitch")
        except Exception as ex:
            logger.warning(ex)
        try:
            keyring.delete_password(KEYRING_SERVICE,"obs")
        except Exception as ex:
            logger.warning(ex)
        
    
    def start(self):
        self.twitch  = get_twitch_irc_client()
        self.connections.add(self.twitch)
        self.obs = get_obs_client()
        self.connections.add(self.obs)
        try:
            asyncio.run(self.handler())
        except KeyboardInterrupt:
            pass