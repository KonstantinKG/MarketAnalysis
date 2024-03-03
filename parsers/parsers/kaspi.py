import asyncio
import datetime
import json
import re
import traceback
import uuid
from logging import Logger
from fake_useragent import UserAgent

import aiohttp
from bs4 import BeautifulSoup

from helpers import Database
from models import Category


class KaspiParser:
    DOMAIN = "https://kaspi.kz/shop"
    HEADERS = {"User-Agent": UserAgent().random}
    SESSION = aiohttp.ClientSession(trust_env=True)
    PRODUCTS = list()
    CATEGORIES = list()

    def __init__(self, logger: Logger, db: Database):
        self._logger = logger
        self._db = db

    async def parse(self):
        url = f"{self.DOMAIN}/c/categories/"
        page = await self.get_page(url=url)
        data = self.get_catalog_json(page=page)
        await self.parse_recursive(category=data)

    async def get_page(self, url: str, **kwargs) -> BeautifulSoup:
        attempts = 3
        try:
            while True:
                async with self.SESSION.get(url, headers=self.HEADERS, **kwargs) as response:
                    content = await response.read()
                return BeautifulSoup(content, "lxml")
        except Exception as e:
            attempts -= 1
            if attempts == 0:
                self._logger.error(f"{e}\n{traceback.format_exc()}")
                raise e

            await asyncio.sleep(1)
            self._logger.error(e)

    @staticmethod
    def get_catalog_json(page: BeautifulSoup):
        for script in page.find_all("script"):
            text = script.get_text()
            if "BACKEND.components.catalog" not in text:
                continue

            clean_text = text.replace('BACKEND.components.catalog =', '')
            clean_text = clean_text.replace("null", "\"\"").replace(";", "").strip()

            last_comma_id = clean_text.rfind(",")
            clean_text = clean_text[:last_comma_id] + clean_text[last_comma_id + 1:]

            pattern = re.compile(r'(\b\w+\b): ')
            json_text = pattern.sub(lambda match: f'"{match.group(1)}":', clean_text)

            return json.loads(json_text)
        return None

    async def parse_recursive(self, category: dict):
        if not category["link"].startswith("c/"):
            return

        if not category["subNodes"]:
            # Parse category
            return

        url = f"{self.DOMAIN}/{category['link']}"
        page = await self.get_page(url=url)
        data = self.get_catalog_json(page=page)

        for sub_category in data["subNodes"]:
            category_id = str(uuid.uuid4())
            sub_category["id"] = category_id
            category = Category(id=category_id, parent_id=category.get("id"), name=sub_category["title"],
                                code=sub_category["code"])
            self.CATEGORIES.append(category)
            await self.parse_recursive(category=sub_category)

    async def parse_leaf_category_products(self, category: dict):
        url = f"{self.DOMAIN}/{category['link']}"
        params = {
            "q": f":category: {category['code']}:availableInZones: Magnum_ZONE1",
            "sort": "relevance",
            "sc": "",
            "page": 2
        }

        page = await self.get_page(url=url, params=params)
