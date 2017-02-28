from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
)
from pyramid.view import (
    forbidden_view_config,
    view_config,
)

from ..models import User


@view_config(route_name='login', 
             renderer='../templates/login.jinja2')
def login(req):
    """Present login form or log user into site."""

    next_url = req.params.get('next', req.referrer) or req.route_url('view_wiki')

    message = ''
    login = ''

    if 'form.submitted' in req.params:
        login = req.params['login']
        password = req.params['password']
        user = req.dbsession.query(User).filter_by(name=login).first()

        if user is not None and user.check_password(password):
            headers = remember(req, user.id)
            return HTTPFound(location=next_url, headers=headers)

        message = 'Failed login'

    return dict(
        message=message,
        url=req.route_url('login'),
        next_url=next_url,
        login=login,
    )


@view_config(route_name='logout')
def logout(req):
    """Log user out and redirect to front page."""

    headers = forget(req)
    next_url = req.route_url('view_wiki')
    return HTTPFound(location=next_url, headers=headers)


@forbidden_view_config()
def forbidden_view(req):
    """Prompt user to log in and then re-visit original page."""

    next_url = req.route_url('login', _query={'next': req.url})
    return HTTPFound(location=next_url)
