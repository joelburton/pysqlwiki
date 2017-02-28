from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.security import Allow, Everyone

from pysqlwiki.views.default import WikiRedirectView
from .models import Page


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('view_wiki', '/')
    config.add_route('view_page', '/{pagename}', factory=page_factory)
    config.add_route('add_page', '/add_page/{pagename}', factory=new_page_factory)
    config.add_route('edit_page', '/{pagename}/edit_page', factory=page_factory)


def new_page_factory(request):
    """Make a new page resource -- but if a matching page already exists, redirect there."""

    pagename = request.matchdict['pagename']

    if request.dbsession.query(Page).filter_by(name=pagename).count() > 0:
        next_url = request.route_url('edit_page', pagename=pagename)
        raise HTTPFound(location=next_url)

    return PageResource(Page(name=pagename))


def page_factory(request):
    """Make existing page resource."""

    pagename = request.matchdict['pagename']
    page = request.dbsession.query(Page).filter_by(name=pagename).first()

    if page is None:
        raise HTTPNotFound

    return PageResource(page)


class PageResource(object):
    """Resource modeling an existing page."""

    def __init__(self, page):
        self.page = page

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, 'role:editor', 'edit'),
            (Allow, self.page.creator_id, 'edit'),
            (Allow, 'role:editor', 'create'),
            (Allow, 'role:basic', 'create'),
        ]
