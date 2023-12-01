import os
import asyncio
from  request_utils import fetch_parallel_requests

# accessing API key from environment variables
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_API_KEY")


class AddressRequester():

    @staticmethod
    def request_url(latitude, longitude):
        return f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longitude},{latitude}.json?access_token={MAPBOX_ACCESS_TOKEN}"

    @staticmethod
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

    @staticmethod
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
                requests.append(
                    AddressRequester.request_url(latitude, longitude))
                longitude += delta
        return requests

    @staticmethod
    def process_results(results):
        return set(AddressRequester.address(response, status) for response, status in results)

    @staticmethod
    async def request(urls, **kwargs):
        return AddressRequester.process_results(await fetch_parallel_requests(urls))

    @staticmethod
    async def request_all_in_rectangle(latitude_min, longitude_min, latitude_max, longitude_max, delta):
        urls = AddressRequester.requests_in_rectangle(
            latitude_min, longitude_min, latitude_max, longitude_max, delta)
        print(f"{len(urls)} requests made")
        results = await fetch_parallel_requests(urls, json_only=True)
        return AddressRequester.process_results(results)


if __name__ == "__main__":
    # asyncio.run does not work without this on windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    res = asyncio.run(AddressRequester.request_all_in_rectangle(
        37.8321415, -121.9867142, 37.8391415, -121.9807142, .0005))
    print(res)
    with open("addresses_for_validation_set.txt", "w") as f:
        f.write("\n".join(res))
    print(len(res))
