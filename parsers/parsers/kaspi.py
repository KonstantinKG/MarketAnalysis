import asyncio
import http
import json
import os
import re
import traceback
import uuid
import chompjs
from logging import Logger

import aiofiles
from fake_useragent import UserAgent

import aiohttp
from bs4 import BeautifulSoup

from helpers import Database
from models import Category, Product
from models.Supplier import Supplier


class KaspiParser:
    DOMAIN = "https://kaspi.kz/shop"
    HEADERS = {"User-Agent": UserAgent().random}
    SESSION = aiohttp.ClientSession(trust_env=True)
    PRODUCTS = list()
    CATEGORIES = list()
    SUPPLIERS = list()

    def __init__(self, config: dict, logger: Logger, db: Database):
        self._categories = dict()
        self._config = config
        self._logger = logger
        self._db = db

    async def parse(self):
        category = {"id": "", "link": "c/categories/"}
        self._categories = await self._db.get_categories_as_dict()
        await self.parse_recursive(category=category)

    async def parse_recursive(self, category: dict):
        if not category["link"].startswith("c/"):
            return

        url = f"{self.DOMAIN}/{category['link']}"
        content = await self.request(url=url)
        page = BeautifulSoup(content, "lxml")
        data = self.get_catalog_json(page=page)

        if not data["categoryInfo"]["subNodes"]:
            self._logger.info(f"Parsing '{data['categoryInfo']['title']}' category products.")
            await self.parse_leaf_category_products(category_id=category["id"], data=data["categoryInfo"])
            await self.upload()
            return

        for sub_category in data["categoryInfo"]["subNodes"]:
            if sub_category["title"] == "Все товары":
                continue

            id = self._categories.get(sub_category["code"])
            if not id:
                id = self.find_next_category_id(parent_category_id=category["id"])
                self._categories[sub_category["code"]] = id

            sub_category["id"] = id
            category_model = Category(
                id=id,
                parent_id=category.get("id"),
                name=sub_category["title"],
                code=sub_category["code"]
            )
            self.CATEGORIES.append(category_model)
            await self.parse_recursive(category=sub_category)

    def find_next_category_id(self, parent_category_id):
        filtered_categories = list(filter(lambda x: len(x) == len(parent_category_id) + 3, self._categories.values()))
        filtered_categories = list(filter(lambda x: x.startswith(parent_category_id), filtered_categories))

        last_category_id = max(filtered_categories) if len(filtered_categories) > 0 else ''
        if not last_category_id:
            return f"{parent_category_id}001"

        category_id = str(int(last_category_id) + 1)
        return self.fill_to_3(category_id)

    @staticmethod
    def fill_to_3(value: str):
        remainder = 3 - len(value) % 3
        return f"{'0' * remainder}{value}"

    async def parse_leaf_category_products(self, category_id: str, data: dict):
        url = "https://kaspi.kz/yml/product-view/pl/results"
        params = {
            "page": 1,
            "q": f":category:{data['code']}:availableInZones:Magnum_ZONE1",
            "text": "",
            "sort": "relevance",
            "qs": "",
            "ui": "d",
            "i": -1,
            "c": 750000000
        }

        referer = f"https://kaspi.kz/shop/c/smartphones/?q={params['q'].replace(':', '%3A').replace(' ', '')}&sort={params['sort']}&sc="
        headers = {"User-Agent": self.HEADERS['User-Agent'], "Referer": referer}

        while params["page"] <= 10:
            data = await self.request(url=url, type="json", params=params, headers=headers)
            for card in data["data"]:
                card["category_id"] = category_id
                await self.parse_product(card=card)
                await asyncio.sleep(0.2)

            params["page"] += 1
            await asyncio.sleep(1)
        return

    async def parse_product(self, card: dict):
        try:
            content = await self.request(url=card["shopLink"])
            page = BeautifulSoup(content, "lxml")
            data = self.get_product_json(page=page)
            if not data:
                return

            image = await self.save_photo(data["galleryImages"][0]["medium"])

            id = await self._db.get_product_id(src_id=data["card"]["id"], name=data["card"]["title"])
            id = id if id else str(uuid.uuid4())

            description = data["description"].replace(" ", "") if data["description"] else None

            try:
                characteristics = str(data["specifications"])
                characteristics = json.dumps(chompjs.parse_js_object(characteristics)) if characteristics else None
            except Exception as e:
                characteristics = None

            product = Product(
                id=id,
                src_id=data["card"]["id"],
                category_id=card["category_id"],
                name=data["card"]["title"],
                image=image,
                rating=data["card"]["rating"],
                description=description,
                characteristics=characteristics,
            )

            card["product_id"] = id
            await self.parse_product_suppliers(card)

            self.PRODUCTS.append(product)
        except Exception as e:
            return

    async def parse_product_suppliers(self, card: dict):
        try:
            url = f"https://kaspi.kz/yml/offer-view/offers/{card['id']}"
            headers = {"Referer": card["shopLink"], "User-Agent": self.HEADERS["User-Agent"]}
            payload = {
                "cityId": "750000000",
                "id": card["id"],
                "merchantUID": "",
                "limit": 5,
                "page": 0,
                "sort": True,
                "product": {
                    "brand": card["brand"],
                    "categoryCodes": card["categoryCodes"],
                    "baseProductCodes": card["baseProductCodes"] if card.get("baseProductCodes") else [],
                    "groups": None
                },
                "zoneId": "Magnum_ZONE1",
                "installationId": "-1"
            }

            data = await self.request(method="post", url=url, type="json", headers=headers, json=payload)
            for offer in data["offers"]:
                supplier = Supplier(
                    id=None,
                    product_id=card["product_id"],
                    name=offer["merchantName"],
                    price=offer["price"],
                    rating=offer["merchantRating"]
                )
                self.SUPPLIERS.append(supplier)
        except Exception as e:
            raise e

    async def request(self, url: str, method: str = "get", type: str = "read", **kwargs, ):
        attempts = 3
        try:
            while True:
                if "headers" not in kwargs.keys():
                    kwargs["headers"] = self.HEADERS.copy()

                async with self.SESSION.request(method=method, url=url, **kwargs) as response:
                    call = getattr(response, type, None)
                    content = await call()
                return content
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

            return chompjs.parse_js_object(text)
        return None

    @staticmethod
    def get_product_json(page: BeautifulSoup):
        for script in page.find_all("script"):
            text = script.get_text()

            if "BACKEND.components.item =" not in text:
                continue

            return chompjs.parse_js_object(text)
        return None

    async def save_photo(self, url: str) -> str | None:
        attempts = 3
        try:
            while True:
                async with self.SESSION.get(url=url) as response:
                    if response.status != 200:
                        raise Exception(f"Incorrect response status {response.status}")

                    file_bytes = await response.read()
                    filename = url.split("/")[-1]
                    filename = filename[:filename.find("?")]

                    save_directory = str(os.path.join(self._config["base_dir"], self._config["files"]))
                    os.makedirs(save_directory, exist_ok=True)
                    file_path = os.path.join(save_directory, filename)

                    db_path = str(os.path.join(self._config["files"], filename))
                    if os.path.exists(file_path):
                        return db_path

                    async with aiofiles.open(file_path, 'wb') as file:
                        await file.write(file_bytes)

                    return db_path

        except Exception as e:
            attempts -= 1
            if attempts == 0:
                self._logger.error(e, traceback.format_exc())
                return None
            self._logger.error(e)

    async def upload(self):
        await self._db.insert(
            table=Category.TABLE,
            columns=Category.COLUMNS,
            data=[[c.__dict__.get(col) for col in Category.COLUMNS] for c in self.CATEGORIES],
            on_conflict=Category.ON_CONFLICT
        )

        await self._db.insert(
            table=Product.TABLE,
            columns=Product.COLUMNS,
            data=[[c.__dict__.get(col) for col in Product.COLUMNS] for c in self.PRODUCTS],
            on_conflict=Product.ON_CONFLICT
        )

        supplier_columns = Supplier.COLUMNS.copy()
        supplier_columns.remove("id")

        await self._db.insert(
            table=Supplier.TABLE,
            columns=supplier_columns,
            data=[[c.__dict__.get(col) for col in supplier_columns] for c in self.SUPPLIERS],
            on_conflict=Supplier.ON_CONFLICT
        )

        self.CATEGORIES.clear()
        self.PRODUCTS.clear()
        self.SUPPLIERS.clear()
