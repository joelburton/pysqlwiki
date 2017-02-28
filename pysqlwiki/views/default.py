import html
import re

from pyramid.view import view_config

from ..views.generic import RedirectView, View, FormView
from ..forms import PageForm
from ..models import Page

WIKI_WORDS_RE = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")


@view_config(route_name="view_wiki")
class WikiRedirectView(RedirectView):
    """Redirect to FrontPage."""

    def get_redirect_url(self):
        return self.req.route_url('view_page', pagename='FrontPage')


@view_config(route_name='view_page',
             renderer='../templates/view.jinja2',
             permission='view')
class PageDisplayView(View):
    """View a wiki page."""

    def __call__(self):
        page = self.context.page

        content = WIKI_WORDS_RE.sub(self.add_link, page.data)
        edit_url = self.req.route_url('edit_page', pagename=page.name)
        return dict(page=page, content=content, edit_url=edit_url)

    def add_link(self, match):
        """Replace a WikiWord with a link to view/add that page."""

        word = match.group(1)
        exists = self.req.dbsession.query(Page).filter_by(name=word).count() > 0
        url = self.req.route_url('view_page' if exists else 'add_page', pagename=word)
        return '<a href="%s">%s</a>' % (url, html.escape(word))


@view_config(route_name='edit_page',
             renderer='../templates/edit.jinja2',
             permission='edit')
@view_config(route_name='add_page',
             renderer='../templates/edit.jinja2',
             permission='create')
class PageAddEditView(FormView):
    """Add/Edit a wiki page."""

    form_class = PageForm

    def is_valid(self, data):
        page = self.context.page
        page.name = data['name']
        page.data = data['body']
        if not page.id:
            page.creator = self.req.user
            self.req.dbsession.add(page)

    def get_success_url(self):
        return self.req.route_url('view_page', pagename=self.context.page.name)

    def get_initial(self):
        return dict(name=self.context.page.name, body=self.context.page.data)

