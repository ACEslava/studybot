import asyncio
import os

from dotenv import load_dotenv

from studybot import StudyBot


def main():
    # Set event loop
    try:
        import uvloop
    except ImportError:
        pass
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Get environment variables
    load_dotenv()
    if os.getenv("DEBUG_MODE") == "true":
        bot_token = os.getenv("BOT_TOKEN_DEV")
    else:
        bot_token = os.getenv("BOT_TOKEN")

    # Run bot
    StudyBot().run(bot_token)


if __name__ == "__main__":
    main()
