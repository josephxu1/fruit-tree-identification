import unittest
from unittest.mock import patch
from street_view_images import StreetViewImageDownloader

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
        expected_url = 'https://maps.googleapis.com/maps/api/streetview/metadata?location=New York City&key=None'
        self.assertEqual(self.downloader.meta_url(address), expected_url)

    def test_generate_meta_urls(self):
        addresses = {'New York City', 'San Francisco'}
        expected_urls = [
            'https://maps.googleapis.com/maps/api/streetview/metadata?location=New York City&key=None',
            'https://maps.googleapis.com/maps/api/streetview/metadata?location=San Francisco&key=None'
        ]
        self.assertEqual(self.downloader.generate_meta_urls(addresses), expected_urls)

    def test_execute_meta_check_valid_addresses(self):
        addresses = {'New York City', 'San Francisco'}
        with patch('RequestUtils.make_requests') as mock_make_requests:
            mock_make_requests.return_value = [
                (MockResponse({'status': 'OK'}),),
                (MockResponse({'status': 'OK'}),)
            ]
            valid_addresses = self.downloader.execute_meta_check(addresses)
            self.assertEqual(valid_addresses, addresses)

    def test_execute_meta_check_invalid_addresses(self):
        addresses = {'New York City', 'San Francisco'}
        with patch('RequestUtils.make_requests') as mock_make_requests:
            mock_make_requests.return_value = [
                (MockResponse({'status': 'INVALID'}),),
                (MockResponse({'status': 'OK'}),)
            ]
            valid_addresses = self.downloader.execute_meta_check(addresses)
            self.assertEqual(valid_addresses, {'San Francisco'})

    def test_download_url(self):
        address = 'New York City'
        expected_url = 'https://maps.googleapis.com/maps/api/streetview?key=None&location=New York City&size=600x400&fov=120'
        self.assertEqual(self.downloader.download_url(address), expected_url)

    def test_generate_download_urls(self):
        valid_addresses = {'New York City', 'San Francisco'}
        expected_urls = [
            'https://maps.googleapis.com/maps/api/streetview?key=None&location=New York City&size=600x400&fov=120',
            'https://maps.googleapis.com/maps/api/streetview?key=None&location=San Francisco&size=600x400&fov=120'
        ]
        self.assertEqual(self.downloader.generate_download_urls(valid_addresses), expected_urls)

    def test_download_images(self):
        valid_addresses = {'New York City', 'San Francisco'}
        with patch('RequestUtils.make_requests') as mock_make_requests:
            mock_make_requests.return_value = [
                (MockResponse(content=b'image1'),),
                (MockResponse(content=b'image2'),)
            ]
            with patch('builtins.open', create=True) as mock_open:
                self.downloader.download_images(valid_addresses)
                mock_open.assert_any_call('output_directory\\New York City.jpg', 'wb')
                mock_open.assert_any_call('output_directory\\San Francisco.jpg', 'wb')
                # Add additional assertions if needed

class MockResponse:
    def __init__(self, json_data=None, content=None):
        self.json_data = json_data
        self.content = content

    def json(self):
        return self.json_data

if __name__ == '__main__':
    unittest.main()