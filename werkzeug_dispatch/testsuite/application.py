# -*- coding: utf-8 -*-
"""
    werkzeug_dispatch.testsuite.application
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests `Application` utility class.

    :copyright: (c) 2014 by Ben Mather.
    :license: BSD, see LICENSE for more details.
"""
import unittest

from werkzeug.test import Client
from werkzeug.testsuite import WerkzeugTestCase

from werkzeug import Response, BaseResponse
from werkzeug.routing import Rule
from werkzeug.exceptions import HTTPException, ImATeapot

from werkzeug_dispatch.views import expose
from werkzeug_dispatch.application import Application


class ApplicationTestCase(WerkzeugTestCase):
    def test_basic(self):
        app = Application()

        app.add_routes(Rule('/', endpoint='index'))

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

        got_request = False
        got_response = False

        def middleware(app):
            def handler(env, start_response):
                nonlocal got_request
                got_request = True

                def handle_start_response(*args, **kwargs):
                    nonlocal got_response
                    got_response = True
                    return start_response(*args, **kwargs)

                app(env, handle_start_response)
            return handler

        app.add_middleware(middleware)

        client = Client(app, BaseResponse)

        client.get('/')

        self.assertTrue(got_request)
        self.assertTrue(got_response)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ApplicationTestCase))
    return suite