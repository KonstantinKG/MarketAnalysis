import sys
import json
import asyncio

import logging.config
import aiohttp_cors
from aiohttp import web

from controllers import EventAnalysisController

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

logging.config.dictConfig(config=config["logger"])
logger = logging.getLogger(name=config["app"])

event_analysis_controller = EventAnalysisController(
    config=config,
    logger=logger
)

app = web.Application()

cors = aiohttp_cors.setup(
    app=app,
    defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })


if __name__ == '__main__':
    if (
            sys.version_info[0] == 3
            and sys.version_info[1] >= 8
            and sys.platform.startswith("win")
    ):
        policy = asyncio.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)

    logger.info(f"Running server on {config['host']}:{config['port']}")
    web.run_app(
        app=app,
        host=config['host'],
        port=config['port']
    )
