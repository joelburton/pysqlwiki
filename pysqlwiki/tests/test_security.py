import unittest
from pyramid.testing import DummyRequest

from ..security import AuthTktAuthenticationPolicy


class TestMyAuthenticationPolicy(unittest.TestCase):
    def test_no_user(self):
        request = DummyRequest()

        policy = AuthTktAuthenticationPolicy(None)
        assert policy.authenticated_userid(request) is None

    def test_authenticated_user(self):
        request = DummyRequest()

        # TODO: there's got to be a better way ...
        policy = AuthTktAuthenticationPolicy('')
        headers = policy.remember(request, 'foo')
        first_cookie = headers[0][1]
        cookie_data = first_cookie.split(";", 1)[0]
        cookie_name, data = cookie_data.split("=", 1)
        request.cookies[cookie_name] = data

        assert policy.authenticated_userid(request) == 'foo'
