import os

# Keyring
KEYRING_SERVICE="AWT|twitch_bot"

# File paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMANDS_FPATH = os.path.join(ROOT_DIR, "commands.json")
EVENTS_FPATH = os.path.join(ROOT_DIR, "events.json")
LOGS_FPATH = os.path.join(ROOT_DIR, "bot.log")
