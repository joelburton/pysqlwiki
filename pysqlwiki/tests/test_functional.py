import transaction
import unittest
# noinspection PyPackageRequirements
import webtest

from ..models.meta import Base
from ..models import User, Page, get_tm_session
from .. import main


class FunctionalTests(unittest.TestCase):
    basic_login = '/login?login=basic&password=basic&next=FrontPage&form.submitted=Login'
    basic_wrong_login = '/login?login=basic&password=nope&next=FrontPage&form.submitted=Login'
    basic_login_no_next = '/login?login=basic&password=basic&form.submitted=Login'
    editor_login = '/login?login=editor&password=editor&next=FrontPage&form.submitted=Login'

    @classmethod
    def setUpClass(cls):
        settings = {
            'sqlalchemy.url': 'sqlite://',
            'auth.secret': 'secret',
            'jinja2.filters': 'route_url = pyramid_jinja2.filters:route_url_filter'
        }
        app = main({}, **settings)
        cls.test_app = webtest.TestApp(app)

        session_factory = app.registry['dbsession_factory']
        cls.engine = session_factory.kw['bind']
        Base.metadata.create_all(bind=cls.engine)

        with transaction.manager:
            dbsession = get_tm_session(session_factory, transaction.manager)
            editor = User(name='editor', role='editor')
            editor.set_password('editor')
            basic = User(name='basic', role='basic')
            basic.set_password('basic')
            page1 = Page(name='FrontPage', data='This is the front page', creator=editor)
            page2 = Page(name='BackPage', data='This is the back page', creator=basic)
            dbsession.add_all([basic, editor, page1, page2])

    @classmethod
    def tearDownClass(cls):
        # noinspection PyUnresolvedReferences
        Base.metadata.drop_all(bind=cls.engine)

    def test_root(self):
        res = self.test_app.get('/', status=302)
        assert res.location, 'http://localhost/FrontPage'

    def test_FrontPage(self):
        res = self.test_app.get('/FrontPage', status=200)
        assert b'FrontPage' in res.body

    def test_nonexistent_page(self):
        self.test_app.get('/SomePage', status=404)

    def test_successful_log_in(self):
        res = self.test_app.get(self.basic_login, status=302)
        assert res.location, 'http://localhost/FrontPage'

    def test_successful_log_in_no_next(self):
        res = self.test_app.get(self.basic_login_no_next, status=302)
        assert res.location, 'http://localhost/'

    def test_failed_log_in(self):
        res = self.test_app.get(self.basic_wrong_login, status=200)
        assert b'login' in res.body

    def test_logout_link_present_when_logged_in(self):
        self.test_app.get(self.basic_login, status=302)
        res = self.test_app.get('/FrontPage', status=200)
        assert b'Logout' in res.body

    def test_logout_link_not_present_after_logged_out(self):
        self.test_app.get(self.basic_login, status=302)
        self.test_app.get('/FrontPage', status=200)
        res = self.test_app.get('/logout', status=302)
        assert b'Logout' not in res.body

    def test_anonymous_user_cannot_edit(self):
        res = self.test_app.get('/FrontPage/edit_page', status=302).follow()
        assert b'Login' in res.body

    def test_anonymous_user_cannot_add(self):
        res = self.test_app.get('/add_page/NewPage', status=302).follow()
        assert b'Login' in res.body

    def test_basic_user_cannot_edit_front(self):
        self.test_app.get(self.basic_login, status=302)
        res = self.test_app.get('/FrontPage/edit_page', status=302).follow()
        assert b'Login' in res.body

    def test_basic_user_can_edit_back(self):
        self.test_app.get(self.basic_login, status=302)
        res = self.test_app.get('/BackPage/edit_page', status=200)
        assert b'Editing' in res.body

    def test_basic_user_can_add(self):
        self.test_app.get(self.basic_login, status=302)
        res = self.test_app.get('/add_page/NewPage', status=200)
        assert b'Editing' in res.body

    def test_editors_member_user_can_edit(self):
        self.test_app.get(self.editor_login, status=302)
        res = self.test_app.get('/FrontPage/edit_page', status=200)
        assert b'Editing' in res.body

    def test_editors_member_user_can_add(self):
        self.test_app.get(self.editor_login, status=302)
        res = self.test_app.get('/add_page/NewPage', status=200)
        assert b'Editing' in res.body

    def test_editors_member_user_can_view(self):
        self.test_app.get(self.editor_login, status=302)
        res = self.test_app.get('/FrontPage', status=200)
        assert b'FrontPage' in res.body

    def test_redirect_to_edit_for_existing_page(self):
        self.test_app.get(self.editor_login, status=302)
        res = self.test_app.get('/add_page/FrontPage', status=302)
        assert b'FrontPage' in res.body
