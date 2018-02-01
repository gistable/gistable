from operator import attrgetter

from sqlalchemy import Table, event, subquery
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql.expression import Executable, ClauseElement

from yeepa.common.util import monkey_patch
from yeepa.backend.models import DBSession, metadata, Base, read_only_metadata

# TODO: rework as per the comments on: http://www.sqlalchemy.org/trac/ticket/2690
# REFACT: override __new__ and ensure that the read_only_metadata is used
class ReflectedTable(Table):
    "Never create or drop this table type, as it represents something the ORM does not manage. Also ensure that you always use the read_only_metadata for these tables."


# REFACT: would be nice if one wouldn't have to instantiate the views to make them known, but the metaclass magic still baffles me, so I'm staying away from it
# REFACT: would be nice to extract this into it's own module that we could depend on
# REFACT: make this something more akin to the table object or the declarative table, no idea how to do that though. :)
class View(object):
    """Only supports queries that have no parameters. 
    Use literal_column() to embedd constants as needed."""
    
    name=None
    on=None
    query=None
    _table=None
    
    def __init__(self, name=None, on=None, query=None, table=None):
        if name is not None:
            self.name = name
        if on is not None:
            self.on = on
        if not isinstance(self.on, tuple):
            self.on = (self.on, )
        if query is not None:
            self.query = query
        if table is not None:
            self._table = table
        
        self.register_events()
    
    def __repr__(self):
        return u"%(class_name)s(name=%(name)r, on=%(on)r, query=%(query)r)" % dict(
            class_name=self.__class__.__name__,
            name=self.name,
            on=self.on,
            query=self.query
        )
    
    def register_events(self):
        for dependency in self._dependencies():
            event.listen(
                dependency,
                'after_create',
                self.create_after_all_dependencies
            )
            event.listen(
                dependency,
                "before_drop",
                self.drop_before_all_dependencies
            )
    
    def _dependencies(self):
        for dependency in self.on:
            if isinstance(dependency, Table):
                yield dependency
            if hasattr(dependency, '__table__'):
                yield dependency.__table__
            # TODO: throw
        
    def create_after_all_dependencies(self, *args, **kwargs):
        if self.is_missing_any_dependency():
            return
        
        CreateView(self.name, self.query)(*args, **kwargs)
        if self._table is not None:
            self._table.dispatch.after_create(*args, **kwargs)
            
    def drop_before_all_dependencies(self, *args, **kwargs):
        if self.is_missing_any_dependency():
            return
        
        if self._table is not None:
            self._table.dispatch.before_drop(*args, **kwargs)
        DropView(self.name)(*args, **kwargs)
    
    def is_missing_any_dependency(self):
        dependendent_table_names = map(attrgetter('name'), self._dependencies())
        inspector = Inspector.from_engine(DBSession.bind)
        return not set(dependendent_table_names).issubset(inspector.get_table_names() + inspector.get_view_names())
    
    @property
    def table(self):
        if self._table is None:
            self._table = ReflectedTable(self.name, read_only_metadata, autoload=True)
        
        return self._table


class CreateView(DDLElement):
    def __init__(self, name, query):
        self.name = name
        self.selectable = query

# REFACT: try making those instance methods
@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
    return "\nCREATE VIEW %s\nAS\n\t%s" % (
         element.name,
         compiler.sql_compiler.process(element.selectable, literal_binds=True)
    )

@compiles(CreateView, 'sqlite')
def visit_create_view(element, compiler, **kw):
    return "\nCREATE VIEW IF NOT EXISTS %s\nAS\n\t%s" % (
         element.name,
         compiler.sql_compiler.process(element.selectable, literal_binds=True)
    )

class DropView(DDLElement):
    def __init__(self, name):
        self.name = name

@compiles(DropView)
def visit_drop_view(element, compiler, **kw):
    return "\nDROP VIEW %s" % (element.name)

@compiles(DropView, 'sqlite')
def visit_drop_view(element, compiler, **kw):
    return "\nDROP VIEW IF EXISTS %s" % (element.name)
