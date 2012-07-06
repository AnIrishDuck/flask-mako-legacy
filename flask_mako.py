import os
from functools import wraps

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from flask import request, session, get_flashed_messages, url_for, g
from flask.signals import template_rendered
from mako.lookup import TemplateLookup
from mako.exceptions import RichTraceback, text_error_template

class TemplateError(RuntimeError):
    """
    A template has thrown an error during rendering. The following properties
    are provided by this exception:

    * ``self.tb``: a ``RichTraceback`` object generated from the exception.
    * ``self.text``: the exception information, generated with
      ``mako.text_error_template``.

    """
    def __init__(self, template):
        self.tb = RichTraceback()
        self.text = text_error_template().render()
        msg = "Error occurred while rendering template '{0}'".format(template)
        msg += "\n" + self.text
        super(TemplateError, self).__init__(msg)

class MakoTemplates(object):
    """
    Extension object that allows Flask applications to render Mako templates.

    """
    def __init__(self, app=None):
        if app:
            self.init_app(self.app)

    def init_app(self, app):
        app.config.setdefault('MAKO_TEMPLATE_DIR', 'templates')

    @property
    def app(self):
        return stack.top.app

    @property
    def lookup(self):
        if not hasattr(self.app, "mako_lookup"):

            templates = self.app.config.get('MAKO_TEMPLATE_DIR')
            cache = self.app.config.get('MAKO_CACHE_DIR', None)
            cache_size = self.app.config.get('MAKO_CACHE_SIZE', -1)
            in_encoding = self.app.config.get('MAKO_INPUT_ENCODING', 'utf-8')
            out_encoding = self.app.config.get('MAKO_OUTPUT_ENCODING', 'utf-8')
            imports = self.app.config.get('MAKO_IMPORTS', None)

            templates = templates if isinstance(templates, list) \
                        else [templates]

            blueprints = getattr(self.app, 'blueprints', {})
            for name, blueprint in blueprints.iteritems():
                if blueprint.template_folder:
                    path = os.path.join(blueprint.root_path,
                                        blueprint.template_folder)
                    if os.path.isdir(path): templates.append(path)

            self.app.mako_lookup = TemplateLookup(directories=templates,
                                                  module_directory=cache,
                                                  collection_size=cache_size,
                                                  input_encoding=in_encoding,
                                                  imports=imports,
                                                  output_encoding=out_encoding)
        return self.app.mako_lookup

    def render(self, template_name, **kwargs):
        """
        Render the given template with standard Flask parameters in addition to
        the specified template `kwargs`.

        """
        template = self.lookup.get_template(template_name)
        try:
            args = {'url_for': url_for,
                    'get_flashed_messages': get_flashed_messages}
            args.update(kwargs)
            self.app.update_template_context(args)
            rv = template.render(**args)
            template_rendered.send(self.app, template=template, context=args)
            return rv
        except:
            raise TemplateError(template_name)

