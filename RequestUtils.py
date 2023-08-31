import asyncio
from aiohttp import ClientSession, ClientConnectorError

#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # asyncio.run does not work without this on windows
class RequestUtils():

    @staticmethod
    async def fetch_html(url: str, session: ClientSession, json_only=False, **kwargs) -> tuple:
        try:
            response = await session.request(method="GET", url=url, **kwargs)
        except ClientConnectorError:
            return (None, 404)
        if json_only:
            return await response.json(), response.status
        return response, response.status

    @staticmethod
    async def _make_requests(urls, json_only=False, **kwargs) -> None:
        async with ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(
                    RequestUtils.fetch_html(url=url, session=session, json_only=json_only, **kwargs)
                )
            results = await asyncio.gather(*tasks)

        return results
    
    @staticmethod
    def make_requests(urls, json_only=False, **kwargs) -> None:
        return asyncio.run(RequestUtils._make_requests(urls,json_only=json_only, **kwargs))