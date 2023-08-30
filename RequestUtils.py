import asyncio
from aiohttp import ClientSession, ClientConnectorError

class RequestUtils():

    @staticmethod
    async def fetch_html(url: str, session: ClientSession, **kwargs) -> tuple:
        try:
            resp = await session.request(method="GET", url=url, **kwargs)
        except ClientConnectorError:
            return (None, 404)
        data = await resp
        return data, resp.status

    @staticmethod
    async def make_requests(urls, **kwargs) -> None:
        async with ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(
                    RequestUtils.fetch_html(url=url, session=session, **kwargs)
                )
            results = await asyncio.gather(*tasks)

        return results