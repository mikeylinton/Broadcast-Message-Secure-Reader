from twitch_bot.bot.bot import Bot
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Twitch Bot")
    parser.add_argument("--factory-reset", action="store_true", default=False, help="Reset all credentials")
    args = parser.parse_args()
    bot = Bot()
    if args.factory_reset:
        bot.reset()
    else:
        bot.start()

