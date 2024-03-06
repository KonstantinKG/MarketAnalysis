import asyncpg
from logging import Logger

from asyncpg import Connection

from models import Category, Product


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

    async def insert(self, data: list, table: str, columns: list, on_conflict='ON CONFLICT DO NOTHING'):
        column_names = ', '.join(columns)
        placeholders = ', '.join(['$' + str(i) for i in range(1, len(columns) + 1)])
        query = f'''INSERT INTO {self._config['connection']['schema']}.{table} ({column_names}) VALUES ({placeholders}) {on_conflict};'''

        conn = await self.create_connection()
        await conn.executemany(query, data)

    async def get_product_id(self, src_id: str, name: str) -> int or None:
        query = f'''SELECT id FROM {Product.TABLE} WHERE src_id = $1 AND name = $2;'''
        conn = await self.create_connection()
        rows = await conn.fetch(query, src_id, name)

        return rows[0][0] if len(rows) > 0 else None

    async def get_category_id(self, code: str) -> str or None:
        query = f'''SELECT id FROM {Category.TABLE} WHERE code = $1;'''
        conn = await self.create_connection()
        rows = await conn.fetch(query, code)

        return rows[0][0] if len(rows) > 0 else None

    async def get_categories_as_dict(self) -> dict:
        query = f'''SELECT id, code FROM {self._config['connection']['schema']}.{Category.TABLE};'''

        conn = await self.create_connection()
        rows = await conn.fetch(query)

        result = {}
        for row in rows:
            result[row[1]] = row[0]

        return result
