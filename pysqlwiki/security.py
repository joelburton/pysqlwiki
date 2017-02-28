from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated
from pyramid.security import Everyone

from .models import User


def groupfinder(userid, request):
    """Get role(s) from user."""

    return [f'role:{request.user.role}']


def user(request):
    """Find user obj in database matching request's user id."""

    user_id = request.unauthenticated_userid

    if user_id is not None:
        return request.dbsession.query(User).get(user_id)


def includeme(config):
    settings = config.get_settings()

    authn_policy = AuthTktAuthenticationPolicy(settings['auth.secret'], groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_request_method(user, reify=True)
