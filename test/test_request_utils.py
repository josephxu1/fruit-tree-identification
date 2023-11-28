import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from aiohttp import ClientSession, ClientConnectorError
from request_utils import fetch_html, _make_requests, fetch_parallel_requests

class TestRequestUtils(unittest.TestCase):

    def test_fetch_html_success(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.status = 200
            mock_request.return_value.json.return_value = {'status': 'OK'}
            asyncio.run(fetch_html('url', ClientSession()))
            mock_request.assert_called_once_with(method='GET', url='url')
            # Add additional assertions if needed
    
    def test_fetch_html_failure(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = ClientConnectorError()
            asyncio.run(fetch_html('url', ClientSession()))
            mock_request.assert_called_once_with(method='GET', url='url')
            # Add additional assertions if needed


if __name__ == '__main__':
    unittest.main()