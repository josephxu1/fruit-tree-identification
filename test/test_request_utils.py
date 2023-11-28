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
import errno
import asyncio
from aiohttp import web
from aiohttp.test_utils import TestServer, unittest_run_loop


class TestRequestUtils(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.session = self.loop.run_until_complete(self.get_session())

    @staticmethod
    async def get_session():
        return ClientSession()

    def tearDown(self):
        pass
        self.loop.run_until_complete(self.session.close())
        self.loop.close()

    def test_fetch_html_success(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.status = 200
            mock_request.return_value.json.return_value = {'status': 'OK'}
            self.loop.run_until_complete(fetch_html('url', ClientSession()))
            mock_request.assert_called_once_with(method='GET', url='url')
            # Add additional assertions if needed

    def test_fetch_html_failure(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = ClientConnectorError(
                os_error=OSError(errno.ENETUNREACH, 'Network is unreachable'), connection_key=None)
            self.loop.run_until_complete(fetch_html('url', ClientSession()))
            mock_request.assert_called_once_with(method='GET', url='url')
            # Add additional assertions if needed

    def test_fetch_html_timeout(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = asyncio.TimeoutError()
            with self.assertRaises(asyncio.TimeoutError):
                self.loop.run_until_complete(fetch_html('url', ClientSession()))

    def test_fetch_html_invalid_url(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = ValueError("Invalid URL")
            with self.assertRaises(ValueError):
                self.loop.run_until_complete(fetch_html('invalid_url', ClientSession()))

    def test_make_requests(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.status = 200
            mock_request.return_value.json.return_value = {'status': 'OK'}
            self.loop.run_until_complete(_make_requests(['url1', 'url2'], ClientSession()))
            mock_request.assert_any_call(method='GET', url='url1')
            mock_request.assert_any_call(method='GET', url='url2')
            # Add additional assertions if needed

    def test_make_requests_exception(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("Mock exception")
            with self.assertRaises(Exception):
                self.loop.run_until_complete(_make_requests(['url1', 'url2'], ClientSession()))

    def test_make_requests_multiple(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.status = 200
            mock_request.return_value.json.return_value = {'status': 'OK'}
            self.loop.run_until_complete(_make_requests(['url1', 'url2', 'url3'], ClientSession()))
            mock_request.assert_any_call(method='GET', url='url1')
            mock_request.assert_any_call(method='GET', url='url2')
            mock_request.assert_any_call(method='GET', url='url3')

    def test_make_requests_empty(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.status = 200
            mock_request.return_value.json.return_value = {'status': 'OK'}
            self.loop.run_until_complete(_make_requests([], ClientSession()))
            mock_request.assert_not_called()

    def test_fetch_parallel_requests(self):
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.status = 200
            mock_request.return_value.json.return_value = {'status': 'OK'}
            self.loop.run_until_complete(fetch_parallel_requests(['url1', 'url2']))
            mock_request.assert_any_call(method='GET', url='url1')
            mock_request.assert_any_call(method='GET', url='url2')
            # Add additional assertions if needed

    def test_fetch_parallel_requests_real_http_requests(self):
        urls = ['https://www.google.com', 'https://www.bing.com']
        responses = self.loop.run_until_complete(fetch_parallel_requests(urls))
        for response in responses:
            self.assertEqual(response[1], 200)


class TestFetchParallelRequestsOrder(unittest.TestCase):
    async def setUpAsync(self):
        self.app = web.Application()
        self.app.router.add_get('/fast', self.fast_response)
        self.app.router.add_get('/slow', self.slow_response)
        self.server = TestServer(self.app)
        await self.server.start_server()

    async def tearDownAsync(self):
        await self.server.close()

    async def slow_response(self, request):
        await asyncio.sleep(1)
        return web.Response(text='slow')

    async def fast_response(self, request):
        return web.Response(text='fast')

    async def test_fetch_parallel_requests_order(self):
        urls = [str(self.server.make_url('/slow')), str(self.server.make_url('/fast'))]
        responses = await fetch_parallel_requests(urls)
        responses_text = [await response.text() for response in responses]
        self.assertEqual(responses_text, ['slow', 'fast'])

    def get_new_ioloop(self):
        return asyncio.new_event_loop()


if __name__ == '__main__':
    unittest.main()
