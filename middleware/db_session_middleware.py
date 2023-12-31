from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Dict, Any, Callable, Awaitable

import aiomysql
from utils.dbconnect import RequestDB



class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, connector: aiomysql.pool.Pool):
        super().__init__()
        self.connector = connector


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.connector.acquire() as connect:
            data['request'] = RequestDB(connect)
            return await handler(event, data)