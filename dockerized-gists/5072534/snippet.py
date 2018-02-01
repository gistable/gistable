""":mod:`sqla_intlist` --- Portable integer list type for SQLAlchemy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the docstring of :class:`IntegerList` type.

"""
import collections
import io

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ColumnElement, case, cast, func
from sqlalchemy.sql.functions import char_length, coalesce
from sqlalchemy.types import Integer, Text, TypeDecorator, TypeEngine

__all__ = ('IntegerList', 'IntegerListComparator',
           'IntegerListHasElementClause')


class IntegerListComparator(TypeEngine.Comparator):
    """The custom comparator which implements :meth:`has_element()`
    predicate method for :class:`IntegerList` type.

    """

    def has_element(self, operand):
        """Returns whether the list contains the ``operand`` as
        its element.

        Example::

            table.c.intlist_col.has_element(123)

        """
        return IntegerListHasElementClause(self.expr, operand)

    def count_elements(self):
        """Returns the number of elements in the list.

        Example::

            table.c.intlist_col.count_elements()

        """
        return IntegerListCountElementsClause(self.expr)


class IntegerList(TypeDecorator):
    """The data type which stores a list of integers.  It provides
    a comparison operator :meth:`~IntegerListComparator.has_element()`,
    and counting operator :meth:`~IntegerListComparator.count_elements()`
    as well.

    It's compiled to the most efficient way of the backend.
    For example, the data type is compiled to :class:`ARRAY
    <sqlalchemy.dialects.postgresql.ARRAY>`, and the comparison operator is
    implemented using PostgreSQL's ``@>`` operator, and the counting operator
    is implemented using ``array_length()`` function.  It means you can index
    the column of this type using GIN if PostgreSQL.

    For other backends, it uses ordinary :class:`~sqlalchemy.types.Text`
    data type and integers are joined by commas e.g. ``',1,2,3,'``, and
    the comparing operator is implemented using ``LIKE`` operator, and
    the counting operator is implemented using complex inefficient
    function calls.

    For example::

        table.c.intlist_col.has_element(123)

    the above expression is compiled to the following SQL expression
    for the most backends:

    .. sourcecode:: sql

       "table".intlist_col LIKE '%,123,%'

    or the following SQL for PostgreSQL:

    .. sourcecode:: sql

       "table".intlist_col @> ARRAY[123]

    """

    impl = Text
    comparator_factory = IntegerListComparator
    python_type = collections.Sequence

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return ARRAY(Integer)
        return Text()

    def bind_processor(self, dialect):
        if dialect.name == 'postgresql':
            return lambda value: value
        def process(value):
            if value is None:
                return
            buffer_ = io.BytesIO()
            buffer_.write(',')
            for num in value:
                buffer_.write(str(num))
                buffer_.write(',')
            return buffer_.getvalue()
        return process

    def result_processor(self, dialect, coltype):
        if dialect.name == 'postgresql':
            return lambda value: value
        def process(value):
            if value is None:
                return None
            return [int(v) for v in value.strip(',').split(',') if v]
        return process

    def copy(self):
        return IntegerList()

    def __repr__(self):
        return '{0.__module__}.{0.__name__}()'.format(type(self))


class IntegerListHasElementClause(ColumnElement):

    def __init__(self, list_operand, element_operand):
        self.list_operand = list_operand
        self.element_operand = element_operand


@compiles(IntegerListHasElementClause)
def visit_integer_list_has_element_clause(element, compiler, **kwargs):
    if isinstance(element.element_operand, ColumnElement):
        el = cast(element.element_operand, Text)
    else:
        el = str(element.element_operand)
    return "{0} LIKE {1}".format(
        compiler.process(element.list_operand),
        compiler.process(cast('%,' + el + ',%', Text))
    )


@compiles(IntegerListHasElementClause, 'postgresql')
def visit_integer_list_has_element_clause_postgres(element, compiler, **kwargs):
    return "{0} @> ARRAY[{1}]".format(
        compiler.process(element.list_operand),
        compiler.process(cast(element.element_operand, Integer))
    )


class IntegerListCountElementsClause(ColumnElement):

    def __init__(self, operand):
        self.operand = operand


@compiles(IntegerListCountElementsClause)
def visit_integer_list_count_elements_clause(element, compiler, **kwargs):
    expr = case(
        {element.operand == None: None, element.operand == '': 0},
        else_=char_length(element.operand) - 1 -
              char_length(func.replace(element.operand, ',', ''))
    )
    return compiler.process(expr)


@compiles(IntegerListCountElementsClause, 'postgresql')
def visit_integer_list_count_elements_clause_postgresql(element, compiler,
                                                        **kwargs):
    expr = case(
        {element.operand == None: None},
        else_=coalesce(func.array_length(element.operand, 1), 0)
    )
    return compiler.process(expr)