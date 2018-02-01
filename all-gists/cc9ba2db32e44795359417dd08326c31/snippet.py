# -*- coding: utf-8 -*-
from inflection import underscore
from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty, joinedload, load_only


class RelationshipPathNode(object):
    def __init__(self, value, parent=None):
        if parent:
            parent.isLeaf = False
        self.value = value
        self.parent = parent
        self.isLeaf = True
        self.load_only = set()

    @property
    def path_from_root(self):
        path = []
        _build_path_from_root(self, path)
        return path

    @property
    def load_only_list(self):
        return list(self.load_only)


def _build_path_from_root(node, path):
    if node.parent:
        _build_path_from_root(node.parent, path)
    path.append(node.value)


def resolve_related(query, model, root, path, load_fields, parent=None):
    field = underscore(root["field"])
    children = root["children"]
    # if the current model has the field being request, and the field is a
    # relationship, add it to the query joins
    if hasattr(model, field) and getattr(model, field) and isinstance(
        getattr(model, field).property,
            RelationshipProperty):
        parent = RelationshipPathNode(field, parent=parent)
        path.append(parent)
        model = getattr(model, field).property.mapper.class_

    elif hasattr(inspect(model).mapper.column_attrs, field):
        # ??? I added this check because I have "placeholder" fields in some of my models.
        if parent:
            parent.load_only.add(field)
        else:
            load_fields.add(field)

    for child in children:
        resolve_related(query, model, child, path, load_fields, parent)

    return path


def get_ast_fields(ast, fragments):
    field_asts = ast.selection_set.selections

    for field_ast in field_asts:
        if isinstance(field_ast, InlineFragment):
            for x in get_ast_fields(field_ast, fragments):
                yield x
            continue

        field_name = field_ast.name.value
        if isinstance(field_ast, FragmentSpread):
            for field in fragments[field_name].selection_set.selections:
                yield {
                    'field': field.name.value,
                    'children': get_ast_fields(field, fragments) \
                        if hasattr(field,
                                   'selection_set') and field.selection_set
                    else []}

            continue

        yield {
            'field': field_name,
            'children': get_ast_fields(field_ast, fragments) \
                if field_ast.selection_set else []}


def optimize_resolve(query, info, model=None):
    """
    Optimize the query.
    
    Usage:
    
    .. code-block:: python

        query = MyModel.get_query(context)
        query = optimize_resolve(query, info, MyModel)
        
    :param query: The query object of the model.
    :type query: BaseQuery
    :param info: graphql resolve info
    :param model: The parent Model
    :type model: db.Model
    :return: The optimized query
    :rtype: BaseQuery
    """
    if not model:
        # ??? trying to be smart here
        # ??? so it can be plugged into your custom connection field class
        model = query.column_descriptions[0]['type']

    path = []
    load_fields = set()
    for field_def in get_ast_fields(info.field_asts[0], info.fragments):
        resolve_related(query, model, field_def, path, load_fields)

    joins = [joinedload(".".join(p.path_from_root)).load_only(*p.load_only_list)
             for p in path if p.isLeaf]
    return query.options(*joins, load_only(*list(load_fields)))
