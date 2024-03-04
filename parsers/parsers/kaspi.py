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
        self._categories = dict()

    async def parse(self):
        category = {"id": None, "link": "c/categories/"}
        # self._categories = await self._db.get_categories_as_dict()
        await self.parse_recursive(category=category)

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

    def get_catalog_json(self, page: BeautifulSoup):
        for script in page.find_all("script"):
            text = script.get_text()
            if "BACKEND.components.catalog" not in text:
                continue

            clean_text = text.replace('BACKEND.components.catalog =', '')
            return self.parse_script_json(text=clean_text)

        return None

    def get_product_json(self, page: BeautifulSoup):
        for script in page.find_all("script"):
            text = script.get_text()

            item_id = text.find("BACKEND.components.item =")
            if not item_id:
                continue

            clean_text = text[item_id:].replace('BACKEND.components.item =', '')
            return self.parse_script_json(text=clean_text)

        return None

    @staticmethod
    def parse_script_json(text: str):
        clean_text = text.replace("null", "\"\"").replace(";", "").strip()

        last_comma_id = clean_text.rfind(",")
        clean_text = clean_text[:last_comma_id] + clean_text[last_comma_id + 1:]

        pattern = re.compile(r'(\b\w+\b): ')
        json_text = pattern.sub(lambda match: f'"{match.group(1)}":', clean_text)

        return json.loads(json_text)

    async def parse_recursive(self, category: dict):
        if not category["link"].startswith("c/"):
            return

        url = f"{self.DOMAIN}/{category['link']}"
        page = await self.get_page(url=url)
        data = self.get_catalog_json(page=page)

        if not data["categoryInfo"]["subNodes"]:
            await self.parse_leaf_category_products(category=data["categoryInfo"])
            return

        for sub_category in data["categoryInfo"]["subNodes"]:
            if sub_category["title"] == "Все товары":
                continue

            id = str(uuid.uuid4())
            # id = self._categories.get(sub_category["code"])
            # if not id:
            #     last_category_id = self.find_next_sub_category_id(sub_category_id=category["id"])
            #     id = int(last_category_id) + 1

            sub_category["id"] = id
            category_model = Category(
                id=id,
                parent_id=category.get("id"),
                name=sub_category["title"],
                code=sub_category["code"]
            )
            self.CATEGORIES.append(category_model)
            await self.parse_recursive(category=sub_category)

    def find_next_sub_category_id(self, sub_category_id):
        return max(list(filter(lambda x: x.startwith(sub_category_id), self._categories.values())))

    async def parse_leaf_category_products(self, category: dict):
        url = f"{self.DOMAIN}/{category['link']}"
        params = {
            "q": f":category: {category['code']}:availableInZones: Magnum_ZONE1",
            "sort": "relevance",
            "sc": "",
            "page": 1
        }

        while True:
            page = await self.get_page(url=url, params=params)
            items = page.find_all("div", class_="item-card")
            if len(items) == 0:
                break

            for item in items:
                link = item.find("a", class_="item-card__name-link")["href"]
                await self.parse_product(url=link)

            params["page"] += 1

    async def parse_product(self, url: str):
        page = await self.get_page(url=url)
        product = await self.get_product_json(page=page)
        print("a")
