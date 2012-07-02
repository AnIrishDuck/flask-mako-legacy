import os, tempfile, unittest
from flask import Flask
from flask.ext.mako import MakoTemplates

basic = """
% for arg in arguments:
    ${arg}
% endfor
"""

error = """
% for arg in arguments:
    ${error}
% endfor
"""

class MakoTemplateTest(unittest.TestCase):
    """ Tests the `flask_mako` templating extension. """

    def setUp(self):
        self.root = root = tempfile.mkdtemp()

        self.template_dir = template_dir = os.path.join(root, "templates")
        os.mkdir(template_dir)

        self.app = app = Flask(__name__)
        app.config.update(
            MAKO_TEMPLATE_DIR=template_dir,
            MAKO_CACHE_DIR=os.path.join(root, "cache"),
            MAKO_CACHE_SIZE=10
        )
        self.mako = mako = MakoTemplates(app)

        for name, template in (('basic', basic), ('error_template', error)):
            with open(os.path.join(template_dir, name), 'w') as f:
                f.write(template)

    def _add_template(self, name, text):
        with open(os.path.join(self.template_dir, name), 'w') as f:
            f.write(text)

    def test_basic_template(self):
        """ Tests that the application can render a template. """
        with self.app.test_request_context():
            result = self.mako.render('basic', arguments=['testing', '123'])
            self.assertTrue('testing' in result)
            self.assertTrue('123' in result)

    def test_standard_variables(self):
        """
        Tests that the variables generally available to Flask Jinja
        templates are also available to Mako templates.

        """
        self._add_template("vars", """
        ${config['MAKO_TEMPLATE_DIR']}
        ${request.args}
        ${session.new}
        ${url_for('test')}
        ${get_flashed_messages()}

        ${injected()}
        """)

        @self.app.route('/test')
        def test(): return "test"

        @self.app.context_processor
        def inject(): return {"injected": lambda: "injected"}

        with self.app.test_request_context():
            result = self.mako.render("vars")

    def test_multiple_dirs(self):
        """ Tests template loading from multiple directories. """
        alt_d = os.path.join(self.root, 'alt_templates')
        os.mkdir(alt_d)
        with open(os.path.join(alt_d, 'alt'), 'w') as f:
            f.write("${alt}")

        td = self.app.config['MAKO_TEMPLATE_DIR']
        self.app.config.update(MAKO_TEMPLATE_DIR=[alt_d, td])
        self.mako = MakoTemplates(self.app)

        with self.app.test_request_context():
            result = self.mako.render('alt', alt='testing')
            self.assertTrue('testing' in result)

    def test_error(self):
        """ Tests that template errors are properly handled. """
        from flask.ext.mako import TemplateError

        with self.app.test_request_context():
            with self.assertRaises(TemplateError) as error:
                self.mako.render('error_template', arguments=['x'])

            e = error.exception
            self.assertTrue('error_template' in e.message)
            self.assertTrue('error_template' in e.text)
            self.assertTrue('line 3' in e.text)

