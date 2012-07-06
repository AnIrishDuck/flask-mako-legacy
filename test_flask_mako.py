import os, tempfile
from unittest import TestCase, skipIf
from contextlib import contextmanager

import flask
from flask import Flask, Blueprint
from flask.ext.mako import MakoTemplates, TemplateError

from mako.exceptions import CompileException

class MakoTemplateTest(TestCase):
    """ Tests the `flask_mako` templating extension. """

    def setUp(self):
        self.root = tempfile.mkdtemp()

    def _add_template(self, name, text, d="templates"):
        template_dir = os.path.join(self.root, d)
        if not os.path.exists(template_dir):
            os.mkdir(template_dir)

        with open(os.path.join(template_dir, name), 'w') as f:
            f.write(text.encode('utf8'))

    @contextmanager
    def test_renderer(self, **kwargs):
        app = Flask(__name__)
        app.config.update(
            MAKO_TEMPLATE_DIR=os.path.join(self.root, "templates"),
            MAKO_CACHE_DIR=os.path.join(self.root, "cache"),
            MAKO_CACHE_SIZE=10
        )
        app.config.update(kwargs)
        with app.test_request_context():
            yield app, MakoTemplates(app)

    def test_encoding(self):
        """ Tests that the Mako templates properly handle Unicode. """
        utf = u'\xA2'
        self._add_template("unicode", utf + u'${arg}')

        with self.test_renderer() as (_, mako):
            result = mako.render('unicode', arg=utf)
            self.assertEqual(utf * 2, result.decode("utf8"))

        with self.assertRaises(CompileException):
            with self.test_renderer(MAKO_INPUT_ENCODING="ascii",
                                    MAKO_CACHE_DIR=None) as (_, mako):
                mako.render("unicode", arg="test")

        with self.assertRaises(TemplateError) as e:
            with self.test_renderer(MAKO_OUTPUT_ENCODING="ascii",
                                    MAKO_CACHE_DIR=None) as (_, mako):
                mako.render('unicode', arg='test')
        self.assertEqual(e.exception.tb.errorname, "UnicodeEncodeError")

    def test_basic_template(self):
        """ Tests that the application can render a template. """
        self._add_template("basic", """
        % for arg in arguments:
            ${arg}
        % endfor
        """)
        with self.test_renderer() as (_, mako):
            result = mako.render('basic', arguments=['testing', '123'])
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

        with self.test_renderer() as (app, mako):

            @app.route('/test')
            def test(): return "test"

            @app.context_processor
            def inject(): return {"injected": lambda: "injected"}

            result = mako.render("vars")

    @skipIf(not flask.signals_available,
            "To test signals, install the blinker library")
    def test_signals(self):
        """ Tests that template rendering fires the right signal. """
        from flask.signals import template_rendered

        self._add_template("signal", "signal template")
        with self.test_renderer() as (app, mako):

            log = []
            def record(*args, **extra):
                log.append(args)
            template_rendered.connect(record, app)

            result = mako.render('signal')

            self.assertEqual(len(log), 1)

    def test_multiple_dirs(self):
        """ Tests template loading from multiple directories. """
        alts = ["alt_a", "alt_b", "alt_c"]
        for alt in alts:
            self._add_template(alt, alt + "${alt}", alt)
            self._add_template(alt, alt + "${alt}", alt)

        alt_dirs = [os.path.join(self.root, d) for d in alts]
        with self.test_renderer(MAKO_TEMPLATE_DIR=alt_dirs) as (_, mako):
            for alt in alts:
                result = mako.render(alt, alt='testing')
                self.assertTrue(alt in result)
                self.assertTrue('testing' in result)

    def test_multiple_apps(self):
        """ Tests that the Mako plugin works with multiple Flask apps. """
        self._add_template("app", "test 1", "alt1")
        self._add_template("app", "test 2", "alt2")
        alt1_dir = os.path.join(self.root, "alt1")
        alt2_dir = os.path.join(self.root, "alt2")

        with self.test_renderer(MAKO_TEMPLATE_DIR=alt1_dir) as (_, mako):
            self.assertEqual(mako.render('app'), 'test 1')
            with self.test_renderer(MAKO_TEMPLATE_DIR=[alt2_dir, alt1_dir],
                                    MAKO_CACHE_DIR=None) as (_, _):
                self.assertEqual(mako.render('app'), 'test 2')

    def test_error(self):
        """ Tests that template errors are properly handled. """
        self._add_template("error_template", """
        % for arg in arguments:
            ${error}
        % endfor
        """)

        with self.test_renderer() as (app, mako):
            with self.assertRaises(TemplateError) as error:
                mako.render('error_template', arguments=['x'])

            e = error.exception
            self.assertTrue('error_template' in e.message)
            self.assertTrue('error_template' in e.text)
            self.assertTrue('line 3' in e.text)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MakoTemplateTest))
    return suite
