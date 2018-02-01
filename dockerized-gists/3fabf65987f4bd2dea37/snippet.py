from docutils import nodes, core, io
from docutils.parsers.rst import Directive

def setup(app):
    app.add_directive('test', TestDirective)
    return {'version': '0.1'}

class TestDirective(Directive):
    def run(self):
        table = nodes.table(cols=2)
        group = nodes.tgroup()
        head = nodes.thead()
        body = nodes.tbody()

        table += group
        group += nodes.colspec(colwidth=6)
        group += nodes.colspec(colwidth=6)
        group += head
        group += body

        row = nodes.row()
        row += nodes.entry('', nodes.paragraph('', nodes.Text('H1')))
        row += nodes.entry('', nodes.paragraph('', nodes.Text('H2')))
        head += row

        row = nodes.row()
        row += nodes.entry('', nodes.paragraph('', nodes.Text('F1')))
        row += nodes.entry('', nodes.paragraph('', nodes.Text('F2')))
        body += row

        return [dump_node_tree(
            u"""
            +------+------+
            | H1   | H2   |
            +======+======+
            | F1   | F2   |
            +------+------+
            """), format_node_tree(table), table]


def format_node_tree(node):
    def is_interesting(value):
        if value is None: return False
        if isinstance(value, bool): return True
        return bool(value)

    def dump_attrs(node, indent):
        str = ''
        for key, value in node.attributes.items():
            if not(is_interesting(value)):
                continue
            str += "\n%s@%s => %s" % (indent, key, value)
        return str

    def dump_children(node, indent):
        str = ''
        for child in node.children:
            str += "\n" + dump(child, indent)
        return str

    def dump(node, indent):
        str = "%s%s" % (indent, node.tagname)

        if node.tagname == '#text':
            str += " => %s" % (node)

        if hasattr(node, 'attributes'):
            str += dump_attrs(node, indent + '  ')
        if hasattr(node, 'children'):
            str += dump_children(node, indent + '  ')
        return str

    text = dump(node, '')
    return nodes.literal_block('', nodes.Text(text))

def dump_node_tree(markup):
    def internals(input_string):
        overrides = {}
        overrides['input_encoding'] = 'unicode'
        output, pub = core.publish_programmatically(
            source_class=io.StringInput, source=input_string,
            source_path=None,
            destination_class=io.NullOutput, destination=None,
            destination_path=None,
            reader=None, reader_name='standalone',
            parser=None, parser_name='restructuredtext',
            writer=None, writer_name='null',
            settings=None, settings_spec=None, settings_overrides=overrides,
            config_section=None, enable_exit_status=None)
        return pub.writer.document

    doc = internals(markup)
    return format_node_tree(doc)
