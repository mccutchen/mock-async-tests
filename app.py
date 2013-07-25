#!/bitly/local/bin/python2.7

import json
import logging

import tornado.gen
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


class BaseFetcher(tornado.web.RequestHandler):

    http_client = tornado.httpclient.AsyncHTTPClient()

    def format_response(self, resp):
        self.set_header('Content-Type', 'application/json')
        return self.finish(json.dumps({
            'code': resp.code,
            'type': resp.headers.get('Content-Type', 'unknown'),
            'content_length': len(resp.body),
        }))


class OldFetcher(BaseFetcher):

    @tornado.web.asynchronous
    def get(self):
        url = self.get_argument('url')
        self.http_client.fetch(url, callback=self.on_response)

    def on_response(self, resp):
        return self.format_response(resp)


class NewFetcher(BaseFetcher):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        url = self.get_argument('url')
        resp = yield self.http_client.fetch(url)
        self.format_response(resp)


class App(tornado.web.Application):

    def __init__(self):
        urls = [
            (r'/oldfetch', OldFetcher),
            (r'/newfetch', NewFetcher),
        ]
        super(App, self).__init__(urls)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(request_callback=App())
    server.listen(9999, address='0.0.0.0')
    logging.info('Listening on http://0.0.0.0:9999')
    tornado.ioloop.IOLoop.instance().start()
