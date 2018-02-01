import itertools
import functools
import fnmatch
import os
from StringIO import StringIO

import yaml
from yaml.parser import ParserError
import voluptuous as V


# env: {match: []}
TopSchema = V.Schema({unicode: {unicode: []}})
# id: {module: [{param: value}]}
StateSchema = V.Schema({unicode: {unicode: [{unicode: object}, unicode]}})
# key: <anything>
PillarSchema = V.Schema({unicode: object})


class Parser(object):
    def load(self, fd):
        return self._parse(yaml.compose(fd))

    def loads(self, text):
        return self._parse(StringIO(text))

    def _parse(self, node):
        return getattr(self, '_parse_' + node.__class__.__name__)(node)

    def _parse_MappingNode(self, node):
        keys = set()
        map = {}
        map_error = functools.partial(ParserError, context='while parsing a mapping')
        for k, v in node.value:
            error = functools.partial(map_error, context_mark=k.start_mark)
            kv = self._parse(k)
            if isinstance(kv, (list, dict)):
                raise error(problem='non-scalar key (%r)' % kv)
            if kv in keys:
                raise error(problem='found duplicate key (%r)' % kv)
            keys.add(kv)
            map[kv] = self._parse(v)
        return map

    def _parse_SequenceNode(self, node):
        return [self._parse(v) for v in node.value]

    def _parse_ScalarNode(self, node):
        tag = node.tag.split(':')
        type = tag[-1]
        # TODO: This is missing some types as per http://yaml.org/type/
        return {
            'int': lambda: int(node.value),
            'str': lambda: node.value,
            'float': lambda: float(node.value),
            'bool': lambda: node.value.lower() == 'true',
            'null': lambda: None,
        }[type]()


def walk(root):
    for base, _, files in os.walk(root):
        for file in files:
            yield os.path.join(base, file)


def main():
    parser = Parser()
    for filename in itertools.chain(walk('pillar'), walk('state')):
        if fnmatch.fnmatch(filename, '*.sls'):
            print(filename)
            try:
                with open(filename) as fd:
                    data = parser.load(fd)
            except ParserError as e:
                print(e)
            try:
                if '/top.sls' in filename:
                    data = TopSchema(data)
                    # print(data)
                elif 'state' in filename and '/top.sls' not in filename:
                    data = StateSchema(data)
                    # print(data)
                elif 'pillar' in filename and '/top.sls' not in filename:
                    data = PillarSchema(data)
            except V.Invalid as e:
                print(data)
                raise


if __name__ == '__main__':
    main()
