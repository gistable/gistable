from ansible import utils, errors
import os
import xml.etree.ElementTree as etree

class LookupModule(object):

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def tostr(self, node):

        if isinstance(node, etree._Element):
            if len(node.getchildren()) == 0:
                return node.text
            return etree.tostring(node)
        return str(node)

    def read_xml(self, filename, dflt=None, xpath=None):

        try:
            xmlreader = etree.parse(filename)
            nodes = xmlreader.findall(xpath)
            values = [self.tostr(node) for node in nodes]
            return values

        except Exception, e:
            raise errors.AnsibleError("xmlfile: %s" % str(e))

        return dflt

    def run(self, terms, inject=None, **kwargs):

        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)

        if isinstance(terms, basestring):
            terms = [ terms ]

        ret = []
        for term in terms:
            params = term.split()
            key = params[0]

            paramvals = {
                'file' : 'ansible.xml',
                'default' : None,
                'xpath' : None,
            }

            # parameters specified?
            try:
                for param in params:
                    name, value = param.split('=')
                    assert(name in paramvals)
                    paramvals[name] = value
            except (ValueError, AssertionError), e:
                raise errors.AnsibleError(e)

            path = utils.path_dwim(self.basedir, paramvals['file'])

            var = self.read_xml(path, paramvals['default'], paramvals['xpath'])

            if var is not None:
                if type(var) is list:
                    for v in var:
                        ret.append(v)
                else:
                    ret.append(var)
        return ret
