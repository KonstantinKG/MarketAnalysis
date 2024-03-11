import asyncpg
from logging import Logger
from asyncpg import Connection
from models import Category, Product
from models.Supplier import Supplier


class Database:
    def __init__(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger
        self._pool = None

    async def create_connection(self) -> Connection:
        return await asyncpg.connect(
            user=self._config['connection']['user'],
            host=self._config['connection']['host'],
            port=self._config['connection']['port'],
            database=self._config['connection']['database'],
            password=self._config['connection']['password']
        )

    async def get_product(self, id: str):
        query = f'''
            SELECT
                p.id,
                p.name,
                image,
                p.rating,
                max(price) as price,
                description
            FROM {Product.TABLE} p
            INNER JOIN {Supplier.TABLE} s on p.id = s.product_id
            WHERE p.id='{id}'
            GROUP BY p.id
        '''

        conn = await self.create_connection()
        row = await conn.fetchrow(query)
        return row

    async def get_products(self, offset: int, limit: int, **kwargs):
        query = f'''
            SELECT
                p.id,
                p.name,
                image,
                p.rating,
                max(price) as price
            FROM {Product.TABLE} p
            INNER JOIN {Supplier.TABLE} s on p.id = s.product_id
            {self.make_product_where(kwargs=kwargs)}
            GROUP BY p.id
            {self.make_product_orderby(kwargs=kwargs)}
            OFFSET {offset}
            LIMIT {limit}
        '''

        conn = await self.create_connection()
        rows = await conn.fetch(query)
        return rows

    async def get_products_count(self, **kwargs):
        query = f'''
            WITH prods AS (
                SELECT p.id
                FROM {Product.TABLE} p
                INNER JOIN {Supplier.TABLE} s on p.id = s.product_id
                {self.make_product_where(kwargs=kwargs)}
                GROUP BY p.id
            )
            SELECT count(*) FROM prods;
        '''

        conn = await self.create_connection()
        row = await conn.fetchrow(query)
        return row[0]

    def make_product_where(self, kwargs):
        category = f"starts_with(category_id, '{kwargs.get('category_id')}')" if kwargs.get("category_id") else None
        price = self._make_price_filter(kwargs.get("price")) if kwargs.get("price") else None

        where = category if category else ''
        if where and price:
            where = f"{where} AND {price}"
        else:
            where = price

        return f"WHERE {where}" if where else ''

    def make_product_orderby(self, kwargs: dict):
        sort = self._make_sort_filter(kwargs.get("sort")) if kwargs.get("sort") else None
        orderby = sort if sort else "relevance DESC"
        return f"ORDER BY {orderby}" if orderby else ''

    async def search_products(self, query: str, after: str or None = None, limit: int = 20):
        condition = f"p.name ilike '%{query}%'"
        condition = f"{condition} AND p.id > '{after}'" if after else condition
        query = f'''
            SELECT p.id, p.name, p.rating 
            FROM {Product.TABLE} p
            INNER JOIN {Supplier.TABLE} s on p.id = s.product_id 
            WHERE {condition}
            GROUP BY p.id
            ORDER BY p.rating DESC, max(s.price) DESC
            LIMIT {limit};
        '''

        conn = await self.create_connection()
        rows = await conn.fetch(query)
        return rows

    async def get_suppliers(self, product_id: str):
        query = f'''
            SELECT
                id,
                name,
                price,
                rating
            FROM {Supplier.TABLE} s
            WHERE product_id='{product_id}'
        '''

        conn = await self.create_connection()
        rows = await conn.fetch(query)
        return rows

    async def get_characteristics(self, product_id: str):
        query = f'''SELECT characteristics FROM {Product.TABLE} WHERE id='{product_id}';'''

        conn = await self.create_connection()
        row = await conn.fetchrow(query)
        return row

    async def get_categories(self, parent_id: str) -> list:
        query = f'''
            SELECT id, name, code
            FROM {Category.TABLE}
            WHERE parent_id = '{parent_id if parent_id else ''}';
        '''
        conn = await self.create_connection()
        rows = await conn.fetch(query)

        return rows

    def _make_sort_filter(self, sort: dict) -> str:
        if sort == "relevance":
            return "relevance DESC"
        elif sort == "rating":
            return "rating DESC"
        elif sort == "cheap":
            return "price ASC"
        elif sort == "expensive":
            return "price DESC"
        else:
            raise Exception("Incorrect sort filter")

    def _make_price_filter(self, price: str) -> str:
        if price == "10":
            return f"price < 10000"
        elif price == "10to50":
            return f"price BETWEEN 10000 AND 50000"
        elif price == "50to100":
            return f"price BETWEEN 50000 AND 100000"
        elif price == "100to150":
            return f"price BETWEEN 100000 AND 150000"
        elif price == "150to200":
            return f"price BETWEEN 150000 AND 200000"
        elif price == "200to500":
            return f"price BETWEEN 200000 AND 500000"
        elif price == "more500":
            return f"price > 500000"
        else:
            raise Exception("Incorrect price filter")
