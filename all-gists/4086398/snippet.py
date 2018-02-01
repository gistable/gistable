class TemplatesTest(TestCase):

    def test_templates(self):
        """Templates can compile properly and there's no mismatched tags"""
        # get app template dirs
        template_dirs = []
        apps = [app for app in settings.INSTALLED_APPS
                    if app.startswith('rh2')]
        for app in apps:
            mod = import_module(app)
            template_dirs.append(path.join(path.dirname(mod.__file__),
                                 'templates'))
        # get template dirs from settings
        for template_dir in settings.TEMPLATE_DIRS:
            template_dirs.append(template_dir)
        # find all templates (*.html and *.txt)
        templates = []
        for template_dir in template_dirs:
            templates += glob.glob('%s/*.html' % template_dir)
            templates += glob.glob('%s/*.txt' % template_dir)
            for root, dirnames, filenames in walk(template_dir):
                for dirname in dirnames:
                    template_folder = path.join(root, dirname)
                    templates += glob.glob('%s/*.html' % template_folder)
                    templates += glob.glob('%s/*.txt' % template_folder)
        for template in templates:
            with open(template, 'r') as f:
                source = f.read()
                # template compilation fails on impaired or invalid blocks tags
                try:
                    Template(source)
                except TemplateSyntaxError, e:
                    raise TemplateSyntaxError('%s in %s' % (e, template))
                # check for badly formated tags or filters
                self.assertEqual(source.count('{%'),
                                 source.count('%}'),
                                 "Found impaired {%% and %%} in %s" % template)
                self.assertEqual(source.count('{{'),
                                 source.count('}}'),
                                 "Found impaired {{ and }} in %s" % template)
