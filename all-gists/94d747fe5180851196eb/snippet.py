import yaml
from yaml.constructor import ConstructorError

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def no_duplicates_constructor(loader, node, deep=False):
    """Check for duplicate keys."""

    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        value = loader.construct_object(value_node, deep=deep)
        if key in mapping:
            raise ConstructorError("while constructing a mapping", node.start_mark,
                                   "found duplicate key (%s)" % key, key_node.start_mark)
        mapping[key] = value

    return loader.construct_mapping(node, deep)

yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_duplicates_constructor)

# Works fine (no duplicate keys)
yaml_data = yaml.load('''
---
foo: bar
baz: qux
'''
)

# Works fine (no duplicate keys on the same level)
yaml_data = yaml.load('''
---
foo:
    bar: baz
    baz: qux
bar:
    bar: baz
    baz: qux
'''
)

# Raises exception (has duplicate keys)
yaml_data = yaml.load('''
---
foo: bar
foo: qux
'''
)
