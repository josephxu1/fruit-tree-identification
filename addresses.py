import os
import asyncio
from aiohttp import ClientSession, ClientConnectorError

MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_API_KEY") #accessing API key from environment variables

#TODO: put these all in a class 
def request_url(latitude, longitude):
    return f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longitude},{latitude}.json?access_token={MAPBOX_ACCESS_TOKEN}"

def address(response, status):
    """extracts address from API response

    Args:
        response (json data): 
        status (int): 

    Returns:
        str: address in standard form
    """
    if status == 200:
        data = response
        
        # Extracting relevant information from the response
        features = data["features"]
        try:
            place_name = features[0]["place_name"]
            return place_name            
        except (KeyError, IndexError):
            return None
    else:
        return f"Request failed with status code: {response.status_code}"

 
def requests_in_rectangle(latitude_min, longitude_min, latitude_max, longitude_max, delta):
    """returns list api requests of a grid of points overlayed on a rectangular region

    Args:
        latitude_min (float): latitude of bottom left corner of the rectangle
        longitude_min (float): longitude of bottom left corner of the rectangle
        latitude_max (float): latitude of top right corner of the rectangle
        longitude_max (float): longitude of top right corner of the rectangle
        delta (float): longitude/latitude distance between between points in grid 

    Returns:
        [str] : list of URLs 
    """
    requests = []
    latitude = latitude_min
    while latitude < latitude_max:
        latitude += delta
        longitude = longitude_min
        while longitude < longitude_max:
            requests.append(request_url(latitude, longitude))
            longitude += delta
    return requests 


def process_results(results):
    return set(address(response, status) for response, status in results)

async def fetch_html(url: str, session: ClientSession, **kwargs) -> tuple:
    try:
        resp = await session.request(method="GET", url=url, **kwargs)
    except ClientConnectorError:
        return (None, 404)
    data = await resp.json()
    return data, resp.status

async def make_requests(urls, **kwargs) -> None:
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                fetch_html(url=url, session=session, **kwargs)
            )
        results = await asyncio.gather(*tasks)

    return process_results(results)
    


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # asyncio.run does not work without this on windows

    urls = requests_in_rectangle(37.8331415, -121.9827142, 37.8391415, -121.9807142, .0005)
    addresses = asyncio.run(make_requests(urls))
    for addy in addresses:
        print(addy)
    print(f"{len(urls)} requests made")
    