import os
import requests


class Downloader:
    def __init__(self, addresses: set, output_directory: str, size: str = '640x640', fov: int = 120):
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

    def check_meta(self, address: str) -> bool:
        # check metadata response to determine if imagery available at address
        meta_base = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
        meta_params = {'key': self.api_key,
                       'location': address}
        meta_response = requests.get(meta_base, params=meta_params)
        return meta_response.json()['status'] == 'OK'

    def download_image(self, address: str) -> requests.Response:
        # request image
        pic_base = 'https://maps.googleapis.com/maps/api/streetview?'
        pic_params = {'key': self.api_key,
                      'location': address,
                      'size': self.size,
                      'fov': self.fov}
        return requests.get(pic_base, pic_params)

    def download_images(self,) -> None:
        # use other class methods to download all images
        self.make_output_dir()
        for addy in self.addresses:
            # only attempt to download image if metadata request returns valid for location
            if self.check_meta(addy):
                print(f'Valid metadata at {addy}')
                image = self.download_image(addy)
                with open(self.output_directory + '\\' + addy + '.jpg', 'wb') as file:
                    file.write(image.content)
            else:
                print(f'Invalid metadata at {addy}')
