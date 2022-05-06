import asyncio
import os

from searchio import SearchIO


def main():
    # Set event loop
    try:
        import uvloop
    except ImportError:
        pass
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Get environment variables
    if os.environ["DEBUG_MODE"] == "true":
        bot_token = os.environ["BOT_TOKEN_DEV"]
    else:
        bot_token = os.environ["BOT_TOKEN"]

    # Run bot
    SearchIO().run(bot_token)


if __name__ == "__main__":
    main()
