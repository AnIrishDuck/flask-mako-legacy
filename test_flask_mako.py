import os, tempfile, unittest

import flask
from flask import Flask
from flask.ext.mako import MakoTemplates, TemplateError

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

    def _make_app(self):
        app = Flask(__name__)
        app.config.update(
            MAKO_TEMPLATE_DIR=self.template_dir,
            MAKO_CACHE_DIR=os.path.join(self.root, "cache"),
            MAKO_CACHE_SIZE=10
        )
        return app

    def setUp(self):
        self.root = root = tempfile.mkdtemp()

        self.template_dir = os.path.join(root, "templates")

        self.app = self._make_app()
        self.mako = MakoTemplates(self.app)

        for name, template in (('basic', basic), ('error_template', error)):
            self._add_template(name, template)

    def _add_template(self, name, text, d="templates"):
        template_dir = os.path.join(self.root, d)
        if not os.path.exists(template_dir):
            os.mkdir(template_dir)

        with open(os.path.join(template_dir, name), 'w') as f:
            f.write(text.encode('utf8'))

    def test_encoding(self):
        """ Tests that the application properly handles Unicode. """
        utf = "\xC2\xA2"
        self._add_template("unicode", utf)

        with self.app.test_request_context():
            self.assertEqual(utf, self.mako.render('unicode'))

        with self.assertRaises(TemplateError):
            app = self.app
            app.config.update(MAKO_OUTPUT_ENCODING='ascii')
            ascii_mako = MakoTemplates(app)
            with self.app.test_request_context():
                ascii_mako.render('unicode')

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

    def test_signals(self):
        """ Tests that template rendering fires the right signal. """
        from flask.signals import template_rendered
        log = []

        def record(*args, **extra):
            log.append(args)
        template_rendered.connect(record, self.app)

        with self.app.test_request_context():
            result = self.mako.render('basic', arguments=[])

        self.assertEqual(len(log), 1)

    if not flask.signals_available:
        test_signals = unittest.skip("To test signals, install the blinker "
                                     "library")(test_signals)

    def test_multiple_dirs(self):
        """ Tests template loading from multiple directories. """
        self._add_template("alt", "${alt}", "alt_templates")
        alt_d = os.path.join(self.root, "alt_templates")

        td = self.app.config['MAKO_TEMPLATE_DIR']
        self.app.config.update(MAKO_TEMPLATE_DIR=[alt_d, td])
        self.mako = MakoTemplates(self.app)

        with self.app.test_request_context():
            result = self.mako.render('alt', alt='testing')
            self.assertTrue('testing' in result)

    def test_error(self):
        """ Tests that template errors are properly handled. """
        with self.app.test_request_context():
            with self.assertRaises(TemplateError) as error:
                self.mako.render('error_template', arguments=['x'])

            e = error.exception
            self.assertTrue('error_template' in e.message)
            self.assertTrue('error_template' in e.text)
            self.assertTrue('line 3' in e.text)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MakoTemplateTest))
    return suite
