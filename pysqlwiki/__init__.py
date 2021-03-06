"""Pyramid Wiki app."""

from pyramid.config import Configurator


# noinspection PyUnusedLocal
def main(global_config, **settings):
    """This function returns a Pyramid WSGI application. """

    config = Configurator(settings=settings)

    config.include('pyramid_jinja2')

    config.include('.models')
    config.include('.routes')
    config.include('.security')

    config.add_static_view('deform_static', 'deform:static/')

    config.scan('.views')

    return config.make_wsgi_app()
