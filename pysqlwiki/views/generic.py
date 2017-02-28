import deform
from pyramid.httpexceptions import HTTPFound


class View:
    """Generic view."""
    def __init__(self, req):
        self.req = req
        self.context = req.context

class RedirectView(View):
    """Generic redirect view."""
    redirect_url = None

    def get_redirect_url(self):
        raise NotImplementedError

    def __call__(self):
        getter = getattr(self, 'get_redirect_url', None)
        url = getter() if getter else self.redirect_url
        return HTTPFound(location=url)


class FormView(View):
    """Generic add/edit view."""

    form_class = None

    def get_success_url(self):
        raise NotImplementedError

    def get_initial(self):
        raise NotImplementedError

    def is_valid(self, appstruct):
        raise NotImplementedError

    def __call__(self):
        form = deform.Form(self.form_class(), buttons=('submit',))
        reqts = form.get_widget_resources()

        if 'submit' in self.req.params:
            try:
                appstruct = form.validate(self.req.POST.items())
            except deform.ValidationFailure as e:
                return {"form": e.render(), "reqts": reqts, "context": self.context}

            self.is_valid(appstruct)

            next_url = self.get_success_url()
            return HTTPFound(location=next_url)

        return {"form": form.render(self.get_initial()),
                "reqts": reqts,
                "context": self.context}

