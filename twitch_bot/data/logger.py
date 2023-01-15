import logging
from twitch_bot.data.consts import ROOT_DIR, LOGS_FPATH
import sys
import os

log_format = "%(asctime)s %(message)s"
date_format = "%H:%M:%S"

if not os.path.exists(ROOT_DIR):
    os.makedirs(ROOT_DIR)


logging.basicConfig(
    filename=LOGS_FPATH,
    format=log_format,
    filemode="w",
    datefmt=date_format,
)

log_level = logging.DEBUG

logger = logging.getLogger()

logger.setLevel(log_level)

# writing to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
handler.setFormatter(
    logging.Formatter(
        fmt=log_format,
        datefmt=date_format,
    )
)
logger.addHandler(handler)
