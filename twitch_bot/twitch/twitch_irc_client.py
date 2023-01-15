import json
from twitch_bot.data.logger import logger
from twitch_bot.data.consts import COMMANDS_FPATH
from dataclasses import dataclass
from twitch_bot.auth.auth import is_expired
from twitch_bot.data.consts import KEYRING_SERVICE
from twitch_bot.data.logger import logger
from twitch_bot.auth.models import TwitchApp, TwitchToken
from twitch_bot.twitch.oauth2 import get_twitch_app, get_twitch_token
import keyring
import json

TWITCH_IRC = "tmi.twitch.tv"

COMMAND_PREFIX = "!"
COMMANDS_STATE = "commands"
ADD_COMMAND = "addcommand"
EDIT_COMMAND = "editcommand"
DELETE_COMMAND = "deletecommand"
LIST_COMMANDS = "commands"

@dataclass
class User:
    name: str
    badges: str
    colour: str
    mod: bool
    subscriber: bool

@dataclass
class Message:
    prefix: str
    user: User
    channel: str
    irc_command: str
    irc_args: str
    text: str
    text_command: str
    text_args: str


def remove_prefix(string, prefix):
    if not string.startswith(prefix):
        return string
    _len = len(prefix)
    return string[_len:]


class TwitchIRCClient:
    def __init__(self, access_token: str, channel: str):
        self.ws = None
        self.protocol = "wss"
        self.host = "irc-ws.chat.twitch.tv"
        self.uri = f"{self.protocol}://{self.host}"
        self.oauth_token = f"oauth:{access_token}"
        self.username = channel
        self.channels = [channel]
        self.command_prefix = COMMAND_PREFIX
        self.state = {}
        self.data = {
            COMMANDS_STATE: COMMANDS_FPATH,
        }

    def load_data(self):
        for _type, file in self.data.items():
            self.read_state(_type, file)

    def read_state(self, _type, file):
        try:
            with open(file, "r") as f:
                self.state[_type] = json.load(f)
        except Exception:
            self.state[_type] = {}

    def write_state(self, _type, file):
        with open(file, "w") as f:
            json.dump(self.state[_type], f)

    async def send_privmsg(self, channel, text):
        await self.send_command(f"PRIVMSG #{channel} :{text}")

    async def send_command(self, command):
        if "PASS" not in command:
            logger.info(f"[ttv] <  {command}")
        await self.ws.send(command + "\r\n")

    async def disconnect(self):
        for channel in self.channels:
            await self.send_privmsg(channel, "See ya!")

    def get_user_from_prefix(self, prefix):
        domain = prefix.split(COMMAND_PREFIX)[0]
        if domain.endswith(f".{TWITCH_IRC}"):
            return domain.replace(f".{TWITCH_IRC}", "")
        if TWITCH_IRC not in domain:
            return domain
        return None

    def get_user_role(self, user):
        if user.mod:
            return 2
        elif user.badges[0].split("/")[0] == "broadcaster" and self.username == user.name:
            return 3
        else:
            return 0

    def get_message_role(self, role):
        role_map = {
            "moderator": 2,
            "broadcaster": 3,
            "": 0,
        }
        return role_map[role.lower()]

    def parse_message(self, received_msg):
        parts = received_msg.split(" ")

        # Message
        prefix = None
        user = None
        channel = None
        text = None
        text_command = None
        text_args = None
        irc_command = None
        irc_args = None

        if parts[0].startswith("@"):
            user_info = {}
            for item in parts.pop(0).lstrip("@").split(";"):
                k, v = item.split("=")
                user_info[k] = v

            user = User(
                name=user_info.get("display-name"),
                badges=user_info.get("badges", "").split(","),
                colour=user_info.get("color"),
                mod=bool(int(user_info.get("mod", 0))),
                subscriber=bool(int(user_info.get("subscriber", 0))),
            )

        if parts[0].startswith(":"):
            prefix = remove_prefix(parts[0], ":")
            if not user:
                user = User(
                    name=self.get_user_from_prefix(prefix),
                    badges=None,
                    colour=None,
                    mod=None,
                    subscriber=None,
                )
            parts = parts[1:]

        text_start = next((idx for idx, part in enumerate(parts) if part.startswith(":")), None)
        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = " ".join(text_parts)
            if text_parts[0].startswith(self.command_prefix):
                text_command = remove_prefix(text_parts[0], self.command_prefix)
                text_args = text_parts[1:]
            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]

        hash_start = next((idx for idx, part in enumerate(irc_args) if part.startswith("#")), None)
        if hash_start is not None:
            channel = irc_args[hash_start][1:]

        message = Message(
            prefix=prefix,
            user=user,
            channel=channel,
            text=text,
            text_command=text_command,
            text_args=text_args,
            irc_command=irc_command,
            irc_args=irc_args,
        )

        return message

    async def handle_command(self, message, text_command, command_content):
        try:
            text = command_content.format(**{"message": message})
            await self.send_privmsg(message.channel, text)
        except IndexError:
            text = f"@{message.user} Your command is missing some arguments!"
            await self.send_privmsg(message.channel, text)
        except Exception as e:
            logger.error(f"[ttv] ! Error while handling command. {message} {command_content}")
            logger.error(f"[ttv] x {e}")

    async def handle_message(self, received_msg):
        if len(received_msg) == 0:
            return

        message = self.parse_message(received_msg)
        logger.info(f"[ttv] > {received_msg}")

        if message.irc_command == "PING":
            await self.send_command(f"PONG :{TWITCH_IRC}")

        if message.irc_command == "PRIVMSG":
            if message.text_command in self.state[COMMANDS_STATE]:
                if self.get_message_role(self.state[COMMANDS_STATE][message.text_command]["role"]) > self.get_user_role(
                    message.user
                ):
                    for channel in self.channels:
                        await self.send_privmsg(channel, f"{message.user} does not have permission for the command {message.text_command}")
                else:
                    await self.handle_command(
                        message,
                        message.text_command,
                        self.state[COMMANDS_STATE][message.text_command]["content"],
                    )


def get_twitch_irc_client() -> TwitchIRCClient:
    keyring_name = "twitch"
    twitch_creds = keyring.get_password(KEYRING_SERVICE, keyring_name)
    if not twitch_creds:
        # First time setup
        twitch_app = get_twitch_app()
        twitch_token = get_twitch_token(twitch_app=twitch_app)
        twitch_channel = input("Twitch channel: ").strip()
        twitch_creds = {
            "app": twitch_app.__dict__,
            "token": twitch_token.__dict__,
            "channel": twitch_channel
        }
        keyring.set_password(KEYRING_SERVICE, keyring_name, json.dumps(twitch_creds))
    else:
        twitch_creds = json.loads(twitch_creds)
        twitch_app = TwitchApp(**twitch_creds["app"])
        twitch_token = TwitchToken(**twitch_creds["token"])
        twitch_channel = twitch_creds["channel"]

    if is_expired(twitch_token.expires_on):
        twitch_token = get_twitch_token(twitch_app, twitch_token)

    twitch_irc_client = TwitchIRCClient(access_token=twitch_token.access_token, channel=twitch_channel)
    twitch_irc_client.load_data()
    return twitch_irc_client