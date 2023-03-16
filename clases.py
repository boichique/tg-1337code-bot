import aiohttp
import asyncio

class TaskReport:
    def __init__(self, id, username, date, level, link, description):
        self.id = id
        self.username = username
        self.date = date
        self.level = level
        self.link = link
        self.description = description


class Session:
    def __init__(self):
        self._session = aiohttp.ClientSession()

    def __del__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.close())

    async def close(self):
        await self._session.close()


