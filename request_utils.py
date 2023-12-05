import asyncio
from aiohttp import ClientSession, ClientConnectorError

async def fetch_html(url: str, session: ClientSession, json_only=False, **kwargs) -> tuple:
    try:
        response = await session.request(method="GET", url=url, **kwargs)
    except ClientConnectorError:
        return (None, 404)
    if json_only:
        return await response.json(), response.status
    return response, response.status


async def _make_requests(urls, json_only=False, **kwargs):
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                asyncio.create_task(fetch_html(url=url, session=session, json_only=json_only, **kwargs))
            )
        results = await asyncio.gather(*tasks)

    return results


async def fetch_parallel_requests(urls, json_only=False, **kwargs):
    return await _make_requests(urls, json_only=json_only, **kwargs)
