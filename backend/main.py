import asyncio
import json
import logging.config
import sys

import aiohttp_cors
from aiohttp import web
from aiohttp_swagger import setup_swagger

from controllers import MarketAnalysisController
from helpers import Database

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

logging.config.dictConfig(config=config["logger"])
logger = logging.getLogger(name=config["app"])

database = Database(config=config, logger=logger)

event_analysis_controller = MarketAnalysisController(
    config=config,
    logger=logger,
    db=database
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


async def get_product(request):
    response = await event_analysis_controller.get_product(request=request)
    return web.json_response(response)


async def get_products(request):
    response = await event_analysis_controller.get_products(request=request)
    return web.json_response(response)


async def get_suppliers(request):
    response = await event_analysis_controller.get_suppliers(request=request)
    return web.json_response(response)


async def get_categories(request):
    response = await event_analysis_controller.get_categories(request=request)
    return web.json_response(response)


async def get_characteristics(request):
    response = await event_analysis_controller.get_characteristics(request=request)
    return web.json_response(response)


async def get_filters(request):
    response = await event_analysis_controller.get_filters(request=request)
    return web.json_response(response)


app.router.add_get('/get/product', get_product)
app.router.add_get('/get/product/suppliers', get_products)
app.router.add_get('/get/product/characteristics', get_characteristics)
app.router.add_get('/get/products', get_products)
app.router.add_get('/get/categories', get_categories)
app.router.add_get('/get/filters', get_filters)

setup_swagger(app, swagger_url="/api/documentation", swagger_from_file="swagger.yaml", ui_version=3)

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
