import json
import urllib

import mock
import tornado.httputil
import tornado.testing

import app


##############################################################################
# Base test class
##############################################################################

class BaseTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return app.App()

    def api_request(self, method, path, params=None, **kwargs):
        params = urllib.urlencode(params or {}, doseq=1)
        url = path

        if params and method in ('GET', 'HEAD'):
            url += '?' + params
            body = None
        else:
            body = params

        resp = self.fetch(url, method=method, body=body, **kwargs)
        return json.loads(resp.body)


##############################################################################
# Non-mocked tests
##############################################################################

class UnmockedTests(BaseTestCase):

    def test_old_fetch(self):
        params = {
            'url': 'http://httpbin.org/status/201',
        }
        resp = self.api_request('GET', '/oldfetch', params)
        assert resp['code'] == 201
        assert resp['type'] == 'text/html; charset=utf-8'
        assert resp['content_length'] == 0

    def test_new_fetch(self):
        params = {
            'url': 'http://httpbin.org/status/201',
        }
        resp = self.api_request('GET', '/newfetch', params)
        assert resp['code'] == 201
        assert resp['type'] == 'text/html; charset=utf-8'
        assert resp['content_length'] == 0


##############################################################################
# Tests mocked the "manual" way, which I'd like to improve
##############################################################################

def make_mock_fetch(status, body, content_type):
    resp = mock.Mock()
    resp.configure_mock(
        status=status,
        body=body,
        headers=tornado.httputil.HTTPHeaders(content_type=content_type))
    # signature matches tornado.httpclient.AsyncHTTPClient.fetch
    def mock_fetch(request, callback=None, **kwargs):
        callback(resp)
    return mock_fetch


class ManuallyMockedTests(BaseTestCase):

    def test_old_fetch(self):
        mock_fetch = make_mock_fetch(201, '', 'text/html; charset=utf-8')
        with mock.patch('app.OldFetcher.http_client.fetch', new=mock_fetch):
            params = {
                'url': 'http://httpbin.org/status/201',
            }
            resp = self.api_request('GET', '/oldfetch', params)
            assert resp['code'] == 201
            assert resp['type'] == 'text/html; charset=utf-8'
            assert resp['content_length'] == 0

    def test_new_fetch(self):
        mock_fetch = make_mock_fetch(201, '', 'text/html; charset=utf-8')
        with mock.patch('app.NewFetcher.http_client.fetch', new=mock_fetch):
            params = {
                'url': 'http://httpbin.org/status/201',
            }
            resp = self.api_request('GET', '/newfetch', params)
            assert resp['code'] == 201
            assert resp['type'] == 'text/html; charset=utf-8'
            assert resp['content_length'] == 0

        
if __name__ == '__main__':
    import unittest
    unittest.main()
