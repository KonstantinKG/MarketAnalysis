import asyncpg
from logging import Logger


class Database:
    def __init__(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger
        self._pool = None

    async def create_connection(self):
        return await asyncpg.connect(
            user=self._config['connection']['user'],
            host=self._config['connection']['host'],
            port=self._config['connection']['port'],
            database=self._config['connection']['database'],
            password=self._config['connection']['password']
        )

    async def insert(self, data: list, table: str, columns: list):
        column_names = ', '.join(columns)
        placeholders = ', '.join(['$' + str(i) for i in range(1, len(columns) + 1)])
        query = f'''INSERT INTO {self._config['schema']}.{table} ({column_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;'''

        conn = await self.create_connection()
        await conn.executemany(query, data)
