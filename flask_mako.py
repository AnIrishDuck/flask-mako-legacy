# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from flask import request, session, get_flashed_messages, url_for, g
from mako.lookup import TemplateLookup

class MakoTemplates(object):
    """
    Extension object that allows Flask applications to render Mako templates.

    """
    def __init__(self, app=None):
        self.app = app
        if self.app is not None:
            self.init_app(self.app)

    def init_app(self, app):
        app.config.setdefault('MAKO_TEMPLATE_DIR', 'templates')

    def create_lookup(self):
        templates = self.app.config.get('MAKO_TEMPLATE_DIR')
        cache = self.app.config.get('MAKO_CACHE_DIR', None)
        cache_size = self.app.config.get('MAKO_CACHE_SIZE', -1)

        templates = templates if isinstance(templates, list) else [templates]

        return TemplateLookup(directories=templates,
                              module_directory=cache,
                              collection_size=cache_size)

    @property
    def lookup(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'mako_lookup'):
                ctx.mako_lookup = self.create_lookup()
            return ctx.mako_lookup

    def render(self, template, **kwargs):
        """
        Render the given template with standard Flask parameters in addition to
        the specified template `kwargs`.

        """
        template = self.lookup.get_template(template)
        return template.render(g=g, request=request,
                               get_flashed_messages=get_flashed_messages,
                               session=session, url_for=url_for, **kwargs)

