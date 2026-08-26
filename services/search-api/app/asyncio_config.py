import asyncio
import sys


def configure_asyncio() -> None:

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
