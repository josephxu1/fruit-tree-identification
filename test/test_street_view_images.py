import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import unittest
from unittest.mock import patch
from street_view_images import StreetViewImageDownloader
import os
from windows_asyncio_utils import windows_run


class TestStreetViewImageDownloader(unittest.TestCase):

    def setUp(self):
        self.downloader = StreetViewImageDownloader('output_directory')

    def test_make_output_dir_success(self):
        with patch('os.mkdir') as mock_mkdir:
            self.downloader.make_output_dir()
            mock_mkdir.assert_called_once_with('output_directory')
            # Add additional assertions if needed

    def test_make_output_dir_failure(self):
        with patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError('Permission denied')
            self.downloader.make_output_dir()
            mock_mkdir.assert_called_once_with('output_directory')
            # Add additional assertions if needed

    def test_meta_url(self):
        address = 'New York City'
        expected_url = f'https://maps.googleapis.com/maps/api/streetview/metadata?location=New York City&key={self.downloader.api_key}'
        self.assertEqual(self.downloader.meta_url(address), expected_url)

    def test_generate_meta_urls(self):
        addresses = ['New York City', 'San Francisco']
        expected_urls = [
            f'https://maps.googleapis.com/maps/api/streetview/metadata?location=New York City&key={self.downloader.api_key}',
            f'https://maps.googleapis.com/maps/api/streetview/metadata?location=San Francisco&key={self.downloader.api_key}'
        ]
        self.assertEqual(self.downloader.generate_meta_urls(addresses), expected_urls)

    async def test_execute_meta_check_valid_addresses(self):
        addresses = {'New York City', 'San Francisco'}
        with patch('request_utils._make_requests') as mock_make_requests:
            mock_make_requests.return_value = [
                (MockResponse({'status': 'OK'}),),
                (MockResponse({'status': 'OK'}),)
            ]
            valid_addresses = await self.downloader.execute_meta_check(addresses)
            self.assertEqual(valid_addresses, addresses)

    async def test_execute_meta_check_invalid_addresses(self):
        addresses = {'New York City', 'San Francisco'}
        with patch('request_utils._make_requests') as mock_make_requests:
            mock_make_requests.return_value = [
                (MockResponse({'status': 'INVALID'}),),
                (MockResponse({'status': 'OK'}),)
            ]
            valid_addresses = await self.downloader.execute_meta_check(addresses)
            self.assertEqual(valid_addresses, {'San Francisco'})

    def test_download_url(self):
        address = 'New York City'
        expected_url = f'https://maps.googleapis.com/maps/api/streetview?key={self.downloader.api_key}&location=New York City&size=600x400&fov=120'
        self.assertEqual(self.downloader.download_url(address), expected_url)

    def test_generate_download_urls(self):
        valid_addresses = ['348 Harper Ln, Danville CA', '669 Adobe Dr, Danville CA']
        expected_urls = [
            f'https://maps.googleapis.com/maps/api/streetview?key={self.downloader.api_key}&location={valid_addresses[0]}&size=600x400&fov=120',
            f'https://maps.googleapis.com/maps/api/streetview?key={self.downloader.api_key}&location={valid_addresses[1]}&size=600x400&fov=120'
        ]
        self.assertEqual(self.downloader.generate_download_urls(valid_addresses), expected_urls)


    async def test_download_images(self):
        valid_addresses = ['348 Harper Ln, Danville CA', '669 Adobe Dr, Danville CA']
        test_output_directory = 'test_output_directory'
        with patch('request_utils._make_requests') as mock_make_requests:
            mock_make_requests.return_value = [
                (MockResponse(content=b'image1'),),
                (MockResponse(content=b'image2'),)
            ]
            test_downloader = StreetViewImageDownloader(test_output_directory)
            with patch('builtins.open', create=True) as mock_open:
                await test_downloader.download_images(valid_addresses)
                print(mock_open.call_args_list())
                mock_open.assert_any_call(os.path.join(test_downloader.output_directory, f'{valid_addresses[0]}.jpg'), 'wb')
                mock_open.assert_any_call(os.path.join(test_downloader.output_directory, f'{valid_addresses[1]}.jpg'), 'wb')
                # Add additional assertions if needed

class MockResponse:
    def __init__(self, json_data=None, content=None):
        self.json_data = json_data
        self.content = content

    def json(self):
        return self.json_data

if __name__ == '__main__':
    windows_run(unittest.main())
