import os
from RequestUtils import RequestUtils

class StreetViewImageDownloader:
    def __init__(self, addresses: set, output_directory: str, size: str = '600x400', fov: int = 120):
        """Initializes downloader
        Args:
            addresses (set): set of addresses generated in addresses.py
            output_directory (str): destination folder for downloaded images
            size (str): pixel resolution of image, width x height, default 600x400
            fov (int): field of view of image, default 120 which is the max
        """
        self.addresses = addresses
        self.fov = 120
        self.output_directory = output_directory
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.size = size
        self.fov = fov

    def make_output_dir(self) -> None:
        # create destination folder for downloaded images
        print('Attempting to make output directory')
        try:
            os.mkdir(self.output_directory)
            print('Successfully created output directory')
        except OSError as error:
            print(f'Failed with error {error}')

    def meta_url(self, address: str) -> str:
        # generate metadata request url given address
        return f"https://maps.googleapis.com/maps/api/streetview/metadata?location={address}&size={self.size}&fov={self.size}&key={self.api_key}"

    def generate_meta_urls(self,) -> list(str):
        # generate list of metadata request urls
        requests = []
        for address in self.addresses:
            requests.append(self.meta_url(address))
        return requests

    def execute_meta_check(self, meta_urls: list(str)) -> None:
        # execute metadata requests and store results 
        # results stored as list of valid addresses in self.valid_addresses
        meta_urls = self.generate_meta_urls()
        meta_results = RequestUtils.make_requests(meta_urls)
        valid_addresses = []
        for address, meta_response in self.addresses,  meta_results:
            if meta_response[0].json()['status'] == 'OK':
                valid_addresses.append(address)
            else:
                print(f'Invalid metadata at {address}.')
        self.valid_addresses = valid_addresses

    def download_url(self, address: str) -> str:
        # generate image request url given address
        return f"https://maps.googleapis.com/maps/api/streetview?key={self.api_key}&location={address}&size={self.size}&fov={self.fov}"
        
    def generate_download_urls(self,) -> list(str):
        # generate list of image request urls
        urls = []
        for address in self.valid_addresses:
            urls.append(self.download_url(address))
        return urls

    def download_images(self, address: str) -> None:
        # Execute image requests using request utils
        # download results to output directory
        self.make_output_dir()
        image_urls = self.generate_download_urls()
        image_results = RequestUtils.make_requests(image_urls)
        for address, image in self.valid_addresses, image_results:
            with open(self.output_directory + '\\' + address + '.jpg', 'wb') as file:
                file.write(image.content)

    