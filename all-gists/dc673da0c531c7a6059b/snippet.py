import sublime
import sublime_plugin

# { "keys": ["alt+shift+p"], "command": "fuzzy_pretty" },

BRACKETS = {
    '{': '}',
    '(': ')',
    '[': ']',
}

SEPS = [
    ';', ',', '\n',
]

OPERATERS = [
    ':', '=',
]


def build(tree, indent=''):
    if indent is False:
        out = ''
        for node in tree:
            if isinstance(node, str):
                out += node
            elif isinstance(node, list):
                out += build(node, indent=False)
        return out
    out = ''
    test = None
    line = ''
    for i, node in enumerate(tree):
        if isinstance(node, str):
            if node in BRACKETS.values():
                out = out[:-len(line)]
                line = line[:-1] + node + '\n'
            elif node in SEPS:
                out = out[:-len(line)]
                line = line[:-1] + node + '\n'
            else:
                line = indent + node + '\n'
        elif isinstance(node, list):
            test = build(node, indent=False)
            if len(line+test) < 80:
                out = out[:-len(line)]
                line = line[:-1] + test + '\n'
            else:
                line = build(node, indent=indent+'  ')
        out += line
    return out


def proc(text):
    buf = ''
    root = []
    context = root
    stacks = []
    brackets = []
    for c in text:
        if len(brackets) > 0 and c == brackets[-1]:
            brackets.pop()
            context.append(buf + c)
            buf = ''
            context = stacks.pop()
        elif c in BRACKETS:
            brackets.append(BRACKETS[c])
            context.append(buf + c)
            buf = ''
            new_context = []
            context.append(new_context)
            stacks.append(context)
            context = new_context
        elif c in SEPS:
            if c == '\n':
                c = ''
            if buf == '' and len(context) > 0:
                context[-1] += c
            elif buf == '' and c == '':
                pass
            else:
                context.append(buf + c)
                buf = ''
        elif buf == '' and c in ' \t':
            pass
        else:
            buf += c
    context.append(buf)
    return build(root)


class FuzzyPrettyCommand(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        view = self.view
        sel = view.sel()[0]
        region = sel
        if sel.empty():
            region = sublime.Region(0, view.size())
        text = view.substr(region)
        text = proc(text)
        view.replace(edit, region, text)
