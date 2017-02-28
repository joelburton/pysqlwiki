import unittest
import transaction

from pyramid import testing
from pyramid.testing import DummyRequest

from ..models import get_tm_session
from ..models import Page, User
from ..models.meta import Base
from ..routes import PageResource
from ..views.default import PageDisplayView, WikiRedirectView, PageAddEditView


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('..models')
        self.config.include('..routes')

        session_factory = self.config.registry['dbsession_factory']
        self.dbsession = get_tm_session(session_factory, transaction.manager)

        self.init_database()

    def init_database(self):
        session_factory = self.config.registry['dbsession_factory']
        engine = session_factory.kw['bind']
        Base.metadata.create_all(engine)

    def tearDown(self):
        testing.tearDown()
        transaction.abort()


class ViewWikiTests(BaseTest):
    def test_it(self):
        request = testing.DummyRequest(dbsession=self.dbsession)
        response = WikiRedirectView(request)()
        assert response.location == 'http://example.com/FrontPage'


class ViewPageTests(BaseTest):
    def test_it(self):
        # add a page to the db
        user = User(name='foo', role='editor')
        page = Page(name='IDoExist', data='Hello CruelWorld IDoExist', creator=user)
        self.dbsession.add_all([page, user])

        # create a request asking for the page we've created
        request = DummyRequest(dbsession=self.dbsession)
        request.context = PageResource(page)

        # call the view we're testing and check its behavior
        info = PageDisplayView(request)()
        assert info['page'] == page
        assert info['content'] == (
            'Hello'
            ' <a href="http://example.com/add_page/CruelWorld">CruelWorld</a>'
            ' <a href="http://example.com/IDoExist">'
            'IDoExist</a>'
        )
        assert info['edit_url'] == 'http://example.com/IDoExist/edit_page'


class AddPageTests(BaseTest):
    def test_it_page_exists(self):
        request = DummyRequest({'submit': True, 'body': 'Hello yo!', 'name': 'AnotherPage'},
                               dbsession=self.dbsession)
        request.user = User(name='foo', role='editor')
        request.context = PageResource(Page(name='AnotherPage'))
        PageAddEditView(request)()
        page_count = self.dbsession.query(Page).filter_by(name='AnotherPage').count()
        assert page_count > 0

    def test_it_not_submitted(self):
        request = DummyRequest(dbsession=self.dbsession)
        request.user = User(name='foo', role='editor')
        request.context = PageResource(Page(name='AnotherPage'))
        info = PageAddEditView(request)()
        assert info['context'].page == request.context.page

    def test_it_submitted(self):
        request = DummyRequest({'submit': True, 'name': 'AnotherPage', 'body': 'Hello yo!'},
                               dbsession=self.dbsession)
        request.user = User(name='foo', role='editor')
        request.context = PageResource(Page(name='AnotherPage'))
        PageAddEditView(request)()
        page = self.dbsession.query(Page).filter_by(name='AnotherPage').one()
        assert page.data == 'Hello yo!'


class EditPageTests(BaseTest):
    def test_it_not_submitted(self):
        user = User(name='foo', role='editor')
        page = Page(name='abc', data='hello', creator=user)
        self.dbsession.add_all([page, user])

        request = DummyRequest(dbsession=self.dbsession)
        request.context = PageResource(page)
        info = PageAddEditView(request)()
        assert info['context'].page == page

    def test_it_submitted(self):
        user = User(name='foo', role='editor')
        page = Page(name='abc', data='hello', creator=user)
        self.dbsession.add_all([page, user])
        self.dbsession.flush()

        request = DummyRequest({'submit': True, 'body': 'Hello yo!', 'name': 'abc'},
                               dbsession=self.dbsession)
        request.context = PageResource(page)
        response = PageAddEditView(request)()
        assert response.location == 'http://example.com/abc'
        assert page.data == 'Hello yo!'
