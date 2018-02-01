import pyparsing as p
import inspect
import pprint


def process(fn, inline=True, badges=True, multiline=True, tag="", mtag="", debug=False, skip_lines=2):
    """
        You can use semicolon tags or specify pyparsing tag in function call
        for example, for @tag:
            '@' + p.Word(p.alphas + '_').setResultsName('tag')
        also use mtag for multiline tags instead number sign tag

        :arg: inline -- enable inlined comments and non-start string tags
        :arg: badges -- enable tags without content
        :arg: multiline -- enable multiline comments
        :arg: tag -- pyparsing spec for custom tag grammatics
        :arg: mtag -- pyparsing spec for custom multiline tag grammatics
        :arg: skip_lines -- how many lines of function source skip before description (default: 2 -- def line and quotes)

        :return: {'inline_tags': {'tag': [{'content': 'content', 'source': 'source line', 'line': 'line num (inside function)'}]}, 'tags': {'tag': ['content']}, 'badges': ['tag']}

        :author: Averrin
        :in_progress:
        :version: 0.4
        :TODO: eval for native types

        #thanks#
            LordKelvin
            LordKelvin
        #thanks#

    """
    docs = {'tags': {}}
    if inline:
        docs['inline_tags'] = {}
    if badges:
        docs['badges'] = []
    tag = tag if tag else ':' + p.Word(p.alphas + '_').setResultsName('tag') + ':'
    mtag = mtag if mtag else '#' + p.Word(p.alphas + '_').setResultsName('tag') + '#'
    line = p.SkipTo(tag).setResultsName('line') +\
        tag.setResultsName('tag') +\
        p.SkipTo(p.StringEnd()).setResultsName('comment')
    multiline = p.SkipTo(mtag) +\
        mtag.setResultsName('tag') +\
        p.SkipTo(mtag).setResultsName('comment')
    doc = inspect.getsourcelines(fn)[0] if inline else fn.__doc__.split('\n')
    desc = []
    desc_end = False
    for i, l in enumerate(doc):
        res = ''
        res = line.searchString(l)

        if res:
            res = res[0]
            tag = res.tag.tag
            if res:
                desc_end = True
                comment = res.comment.strip()
                code = str(res.line[0]).strip('# \t')
                if comment:
                    if code and inline:  # :inline: works if turn on (and parsed with source line)
                        if tag not in docs['inline_tags']:
                            docs['inline_tags'][tag] = []
                        docs['inline_tags'][tag].append({'content': comment, 'source': code, 'line': i})
                    else:
                        if tag not in docs['tags']:
                            docs['tags'][tag] = []
                        docs['tags'][tag].append(comment)
                elif badges:
                    docs['badges'].append(tag)

        elif i > skip_lines and not desc_end:
            desc.append(l.strip())
    docs['desc'] = desc

    if multiline:
        res = multiline.searchString(fn.__doc__)
        for ml in res:
            tag = ml.tag.tag
            comment = ml.comment[0]
            if comment:
                if tag not in docs['tags']:
                    docs['tags'][tag] = []
                for x in comment.split('\n'):
                    if x.strip():
                        docs['tags'][tag].append(x.strip())
    return docs


if __name__ == '__main__':
    # docs = {}
    # locs = dict(**locals())
    # fns = [f for f in locs if
    #                 all(getattr(locs[f], "__%s__" % attr, None)
    #                     for attr in ("doc", "call"))]
    # for fn in fns:
    # pprint.pprint(process(process, tag='@' + p.Word(p.alphas + '_').setResultsName('tag')))
    pprint.pprint(process(process))
    # print pprint.pprint(process(process, badges=False))
    # process(process)