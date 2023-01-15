import base64
import hashlib
import json
from twitch_bot.data.logger import logger
from twitch_bot.obs.actions import set_scene_item_transform
from twitch_bot.data.consts import KEYRING_SERVICE
import keyring
from getpass import getpass

class ObsClient:
    def __init__(self, port: int, token: str):
        self.ws = None
        self.protocol = "ws"
        self.host = "localhost"
        self.port = port
        self.uri = f"{self.protocol}://{self.host}:{self.port}"
        self._token = token
        self.actions = {
            "sceneItemTransform": set_scene_item_transform,
        }

    async def send_request(self, request_type, request_data):
        request = {
            "op": 6,
            "d": {
                "requestType": request_type,
                "requestId": "",
                "requestData": request_data,
            },
        }
        await self.ws.send(json.dumps(request))

    async def disconnect(self):
        self.ws.close()

    async def handle_event(self, data):
        event_type = data.get("eventType")
        event_intent = data.get("eventIntent")
        event_data = data.get("eventData")
        logger.info(f"[obs] > {event_type} {event_intent} {event_data}")

    async def _send_identify(self, data):

        identify_message = {
            "op": 1,
            "d": {
                "rpcVersion": data["rpcVersion"],
            },
        }
        authentication = data.get("authentication")
        if authentication:
            secret = base64.b64encode(
                hashlib.sha256((self._token + authentication["salt"]).encode("utf-8")).digest()
            )
            identify_message["d"]["authentication"] = base64.b64encode(
                hashlib.sha256(secret + authentication["challenge"].encode("utf-8")).digest()
            ).decode("utf-8")

        await self.ws.send(json.dumps(identify_message))

    async def handle_message(self, received_msg):
        received_msg = json.loads(received_msg)
        data = received_msg.get("d")
        op_code = received_msg.get("op")
        if op_code == 7 or op_code == 9:  # RequestResponse or RequestBatchResponse
            logger.debug(received_msg)
        elif op_code == 5:  # Event
            await self.handle_event(data)
        elif op_code == 0:  # Hello
            await self._send_identify(data)
        elif op_code == 2:  # Identified
            logger.info("[obs] > Connected!")
        else:
            logger.debug(received_msg)


def get_obs_client() -> ObsClient:
    keyring_name = "obs"
    obs_creds = keyring.get_password(KEYRING_SERVICE, keyring_name)
    if not obs_creds:
        port = input("OBS Webhook port (4455 by default): ").strip()
        if not port:
            port = "4455"
        token = getpass(prompt="OBS Webhook password (Tools > obs-websocket Settings): ").strip()
        if not token:
            token = ""
        obs_creds = {
            "token": token,
            "port": port,
        }
        keyring.set_password(KEYRING_SERVICE,"obs",json.dumps(obs_creds))
    else:
        obs_creds = json.loads(obs_creds)
        port = obs_creds["port"]
        token = obs_creds["token"]
    obs_client = ObsClient(port=int(port), token=token)
    return obs_client