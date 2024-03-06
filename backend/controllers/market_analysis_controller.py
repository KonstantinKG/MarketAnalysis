import json
import traceback
from logging import Logger

from aiohttp.web_request import Request

from helpers import Database


class MarketAnalysisController:
    def __init__(self, config: dict, logger: Logger, db: Database):
        self._config = config
        self._logger = logger
        self._db = db

    @staticmethod
    def response(data) -> dict:
        return {"data": data}

    @staticmethod
    def error(errors) -> dict:
        return {"errors": errors}

    async def get_product(self, request: Request):
        try:
            id = request.query.get("id")

            product = await self._db.get_product(id=id)
            return self.response(data={
                "id": product[0],
                "name": product[1],
                "image": product[2],
                "rating": product[3],
                "price": product[4],
                "description": product[5]
            })
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")

    async def get_products(self, request: Request):
        try:
            page = int(request.query.get("page"))
            sort = request.query.get("sort")
            price = request.query.get("price")
            category_id = request.query.get("category_id")

            limit = 20
            offset = (page - 1) * limit
            total = await self._db.get_products_count(sort=sort, price=price, category_id=category_id)
            pages = int(total / limit + (total % 1 if limit > 0 else 0))

            products = await self._db.get_products(offset=offset, limit=limit, sort=sort, price=price, category_id=category_id)

            return self.response(data={
                "total": pages,
                "current": page,
                "data": [
                    {
                        "id": row[0],
                        "name": row[1],
                        "image": row[2],
                        "rating": row[3],
                        "price": row[4]
                    }
                    for row in products
                ]
            })
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")

    async def get_suppliers(self, request: Request):
        try:
            product_id = request.query.get("product_id")
            suppliers = await self._db.get_suppliers(product_id=product_id)
            return self.response(data=[
                {
                    "id": row[0],
                    "name": row[1],
                    "price": row[2],
                    "rating": row[3]
                }
                for row in suppliers
            ])
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")

    async def get_characteristics(self, request: Request):
        try:
            product_id = request.query.get("product_id")
            row = await self._db.get_characteristics(product_id=product_id)
            return self.response(data=json.loads(row[0]) if row[0] else {})
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")

    async def get_categories(self, request: Request):
        try:
            parent_id = request.query.get("id")
            categories = await self._db.get_categories(parent_id=parent_id)
            return self.response(data=[
                {
                    "id": cat[0],
                    "name": cat[1],
                    "code": cat[2]
                }
                for cat in categories
            ])
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")

    async def get_filters(self, request: Request):
        try:
            return self.response(data={
                "sort": [
                    {
                        "id": "relevance",
                        "name": "Новинки"
                    },
                    {
                        "id": "rating",
                        "name": "Высокий рейтинг"
                    },
                    {
                        "id": "cheap",
                        "name": "Сначала дешевые"
                    },
                    {
                        "id": "expensive",
                        "name": "Сначала дорогие"
                    }
                ],
                "price": [
                    {
                        "id": "10",
                        "name": "до 10 000 т"
                    },
                    {
                        "id": "10to50",
                        "name": "10 000 - 49 999 т"
                    },
                    {
                        "id": "50to100",
                        "name": "50 000 - 99 999 т"
                    },
                    {
                        "id": "100to150",
                        "name": "100 000 - 149 999 т"
                    },
                    {
                        "id": "150to200",
                        "name": "150 000 - 199 999 т"
                    },
                    {
                        "id": "200to500",
                        "name": "200 000 - 499 999 т"
                    },
                    {
                        "id": "more500",
                        "name": "более 500 000 т"
                    }
                ]
            })
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")

