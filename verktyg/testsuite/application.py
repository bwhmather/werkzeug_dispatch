"""
    verktyg.testsuite.application
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests `Application` utility class.

    :copyright: (c) 2014 by Ben Mather.
    :license: BSD, see LICENSE for more details.
"""
import unittest

from werkzeug.test import Client
from werkzeug.testsuite import WerkzeugTestCase

from werkzeug import Response, BaseResponse
from werkzeug.exceptions import HTTPException, NotFound, ImATeapot

from verktyg.views import expose
from verktyg.routing import Route
from verktyg.application import Application


class ApplicationTestCase(WerkzeugTestCase):
    def test_basic(self):
        app = Application()

        app.add_routes(Route('/', endpoint='index'))

        @expose(app.dispatcher, 'index')
        def index(app, request):
            return Response('Hello World')

        client = Client(app, BaseResponse)

        resp = client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data(), b'Hello World')

    def test_exception_handlers(self):
        app = Application()

        @app.exception_handler(BaseException)
        def default_handler(app, req, exception):
            return Response('default handler', status=500)

        @app.exception_handler(HTTPException)
        def werkzeug_handler(app, req, exception):
            return Response('werkzeug handler', exception.code)

        @app.expose(route='/raise_execption')
        def raise_exception(app, req):
            raise Exception()

        @app.expose(route='/raise_key_error')
        def raise_key_error(app, req):
            raise KeyError()

        @app.expose(route='/raise_teapot')
        def raise_teapot(app, req):
            raise ImATeapot()

        client = Client(app, BaseResponse)

        resp = client.get('/raise_execption')
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.get_data(), b'default handler')

        resp = client.get('/raise_key_error')
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.get_data(), b'default handler')

        resp = client.get('/raise_teapot')
        self.assertEqual(resp.status_code, 418)
        self.assertEqual(resp.get_data(), b'werkzeug handler')

    def test_middleware(self):
        app = Application()

        @app.expose(route='/')
        def index(app, req):
            return Response()

        results = dict(
            got_request=False,
            got_response=False,
        )

        def middleware(app):
            def handler(env, start_response):
                results['got_request'] = True

                def handle_start_response(*args, **kwargs):
                    results['got_response'] = True
                    return start_response(*args, **kwargs)

                app(env, handle_start_response)
            return handler

        app.add_middleware(middleware)

        client = Client(app, BaseResponse)

        client.get('/')

        self.assertTrue(results['got_request'])
        self.assertTrue(results['got_response'])

    def test_exception_content_type(self):
        app = Application()

        @app.exception_handler(HTTPException)
        def default_handler(app, req, exception):
            return Response('default handler', status=exception.code)

        @app.exception_handler(HTTPException, content_type='text/json')
        def default_json_handler(app, req, exception):
            return Response(
                '{"type": "json"}',
                status=exception.code,
                content_type='text/json'
            )

        @app.exception_handler(NotFound, content_type='text/html')
        def html_not_found_handler(app, req, exception):
            return Response('pretty NotFound', status=exception.code)

        @app.expose(route='/raise_418')
        def raise_418(app, req):
            raise ImATeapot()

        @app.expose(route='/raise_404')
        def raise_404(app, req):
            raise NotFound()

        client = Client(app, BaseResponse)

        resp = client.get('/raise_418')
        self.assertEqual(resp.status_code, 418)
        self.assertEqual(resp.get_data(), b'default handler')

        resp = client.get('raise_418', headers=[('Accept', 'text/json')])
        self.assertEqual(resp.status_code, 418)
        self.assertEqual(resp.get_data(), b'{"type": "json"}')
        self.assertEqual(resp.headers['Content-Type'], 'text/json')

        # 404 error has a pretty html representation but uses default renderer
        # for json
        resp = client.get('/raise_404', headers=[('Accept', 'text/html;')])
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.get_data(), b'pretty NotFound')

        resp = client.get('raise_404', headers=[('Accept', 'text/json')])
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.get_data(), b'{"type": "json"}')
        self.assertEqual(resp.headers['Content-Type'], 'text/json')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ApplicationTestCase))
    return suite
