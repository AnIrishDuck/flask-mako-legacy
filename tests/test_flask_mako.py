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
    ${arg}
% endfor
"""

class MakoTemplateTest(unittest.TestCase):
    """ Tests the `flask_mako` templating extension. """

    def setUp(self):
        self.root = root = tempfile.mkdtemp()

        template_dir = os.path.join(root, "templates")
        os.mkdir(template_dir)

        self.app = app = Flask(__name__)
        app.config.update(
            MAKO_TEMPLATE_DIR=template_dir,
            MAKO_CACHE_DIR=os.path.join(root, "cache"),
            MAKO_CACHE_SIZE=10
        )
        self.mako = mako = MakoTemplates(app)

        for name, template in (('basic', basic), ('error', error)):
            with open(os.path.join(template_dir, name), 'w') as f:
                f.write(template)

    def test_basic_template(self):
        """ Tests that the application can render a template. """
        with self.app.test_request_context():
            result = self.mako.render('basic', arguments=['testing', '123'])
            self.assertTrue('testing' in result)
            self.assertTrue('123' in result)

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

