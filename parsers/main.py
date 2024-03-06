import asyncio
import json
import logging.config
import os
import time
import traceback
from logging import Logger

from helpers import Database
from parsers.kaspi import KaspiParser

config: dict
logger: Logger


def timer(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        value = await func(*args, **kwargs)
        print(f"Parser end up in: {time.time() - start}")
        return value

    return wrapper


@timer
async def main():
    global config, logger

    with open("config.json", 'r', encoding='utf-8') as file:
        config = json.load(file)

    base_dir = os.path.dirname(__file__)
    config["base_dir"] = os.path.join(base_dir, "../")

    logging.config.dictConfig(config=config["logger"])
    logger = logging.getLogger(name=config["app"])

    db = Database(config=config, logger=logger)

    kaspi_parser = KaspiParser(config=config, logger=logger, db=db)

    try:
        logger.info(f"Parser started")
        await kaspi_parser.parse()
    except Exception as err:
        logger.fatal(f"Parser failed with error {err}\nTRACEBACK: {traceback.format_exc()}")
    finally:
        await close_connections()


async def close_connections():
    await asyncio.sleep(0)


if __name__ == '__main__':
    asyncio.run(main())
