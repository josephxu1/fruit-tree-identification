import asyncio
import os
from request_utils import fetch_parallel_requests
import aiohttp

class StreetViewImageDownloader:
    SIZE = '600x400'
    FOV = 120

    def __init__(self, output_directory: str):
        """Initializes downloader
        Args:
            output_directory (str): destination folder for downloaded images
        """
        self.output_directory = output_directory
        self.api_key = os.getenv("GOOGLE_API_KEY")

    def make_output_dir(self) -> None:
        # create destination folder for downloaded images
        # if folder already exists, do nothing
        print('Attempting to make output directory')
        try:
            os.makedirs(self.output_directory, exist_ok=True)
            print('Successfully created output directory')
        except OSError as error:
            print(f'Failed with error {error}')

    def meta_url(self, address: str) -> str:
        # generate metadata request url given address
        return f"https://maps.googleapis.com/maps/api/streetview/metadata?location={address}&key={self.api_key}"

    def generate_meta_urls(self, addresses: set) -> list[str]:
        # generate list of metadata request urls
        requests = []
        for address in addresses:
            requests.append(self.meta_url(address))
        return requests

    async def execute_meta_check(self, addresses: set) -> list[str]:
        # execute metadata requests and store results 
        # results stored as list of valid addresses
        meta_urls = self.generate_meta_urls(addresses)
        meta_results = await fetch_parallel_requests(meta_urls)
        valid_addresses = []
        for address, meta_response in zip(addresses, meta_results):
            json_response = await meta_response[0].json()
            print(json_response)
            if json_response['status'] == 'OK':
                valid_addresses.append(address)
                print(f'Valid metadata at {address}.')
            else:
                print(f'Invalid metadata at {address}.')
        return valid_addresses

    def download_url(self, address: str, size: str = None, fov: int = None) -> str:
        # generate image request url given address
        size = size or self.SIZE
        fov = fov or self.FOV
        return f"https://maps.googleapis.com/maps/api/streetview?key={self.api_key}&location={address}&size={size}&fov={fov}"
        
    def generate_download_urls(self, valid_addresses: list[str], size: str = None, fov: int = None) -> list[str]:
        # generate list of image request urls
        size = size or self.SIZE
        fov = fov or self.FOV
        urls = []
        for address in valid_addresses:
            urls.append(self.download_url(address, size, fov))
        return urls

    async def download_images(self, valid_addresses: list[str], size: str = None, fov: int = None) -> None:
        # Execute image requests using request utils
        # download results to output directory
        if not valid_addresses:
            print('No valid addresses to download')
            return
        size = size or self.SIZE
        fov = fov or self.FOV
        self.make_output_dir()
        image_urls = self.generate_download_urls(valid_addresses, size, fov)

        async def download_image(url: str, output_path: str) -> None:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    with open(output_path, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
                            print(f'chunk written on {output_path}')

        tasks = []
        for url, address in zip(image_urls, valid_addresses):
            output_path = os.path.join(self.output_directory, f"{address}.jpg")
            task = download_image(url, output_path)
            tasks.append(task)
        await asyncio.gather(*tasks)

async def main():
    downloader = StreetViewImageDownloader('validation_images')
    input_path = "./addresses_for_validation_set.txt"
    with open(input_path, "r") as f:
        addresses = f.read().splitlines()
    
    valid_addresses = await downloader.execute_meta_check(set(addresses))

    await downloader.download_images(valid_addresses)

if __name__ == '__main__':
    # asyncio.run does not work without this on windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    