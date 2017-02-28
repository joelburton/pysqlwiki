import unittest

import transaction
from pyramid import testing

from ..models import User
from ..models import get_tm_session
from ..models.meta import Base


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite://'
        })
        self.config.include('..models')
        self.config.include('..routes')

        session_factory = self.config.registry['dbsession_factory']
        self.session = get_tm_session(session_factory, transaction.manager)

        self.init_database()

    def init_database(self):
        session_factory = self.config.registry['dbsession_factory']
        engine = session_factory.kw['bind']
        Base.metadata.create_all(engine)

    def tearDown(self):
        testing.tearDown()
        transaction.abort()


class TestSetPassword(BaseTest):
    def test_password_hash_saved(self):
        user = User(name='foo', role='bar')
        assert not user.password_hash

        user.set_password('secret')
        assert user.password_hash


class TestCheckPassword(BaseTest):
    def test_password_hash_not_set(self):
        user = User(name='foo', role='bar')
        assert not user.password_hash

        assert not user.check_password('secret')

    def test_correct_password(self):
        user = User(name='foo', role='bar')
        user.set_password('secret')
        assert user.password_hash
        assert user.check_password('secret')

    def test_incorrect_password(self):
        user = User(name='foo', role='bar')
        user.set_password('secret')
        assert user.password_hash
        assert not user.check_password('incorrect')
