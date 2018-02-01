r"""
    sqlassist
    ~~~~~~~~~
    
    v0.3
    
    sections of code taken from :
        - Mike Orr's package 'sqlahelper'
        - Mike Bayer's blog post 'Django-style Database Routers in SQLAlchemy'
        
    originally based on findmeon's pylons based opensocialnetwork library
    
    
    About
    =====
    The challenge is to provide for both:
        1. Reflecting Tables ( ie, not authoring a bunch of python class information for dozens of existing database tables )
        2. Supporting multiple database connections ( read, write, log, etc )
    
    Support for Declared Tables happened in v0.3
    
    
    TODO
    ====
    
    1.  -- this is really ugly , it's patched together from a few different projects that work under sqlalchemy .4/.5
        -- this does work in .6/.7, but it doesn't integrate anything new
        fixing

    2.  ------- we don't use the new zope transaction stuff, which most of the pyramid app developers seem to like.
        fixed
    
    3.  ------- the way initialization works is wonky.  init_engine calls a bunch of orm.sessionmaker things that should be configurable
        fixed
    
    4.  ------- there are two registries - engine and session. sigh.
        fixed
    
    5.  still playing with reflected tables , both the __sa_stash__ storage and how they're autoloaded
    
    6.  -- there's a bunch of legacy stuff that hasn't been used/integrated.  ie: under pylons i had middleware that would kill all the dbsessions on exit.  the supporting functions are here, but not used
        fixing
    
    
    
    Usage
    =====
    
    in your env.ini you specify multiple sqlalchemy urls, which might be to different dbs , or the same db but with different permissions

        sqlalchemy_reader.url = postgres://myapp_reader:myapp@localhost/myapp
        sqlalchemy_writer.url = postgres://myapp_writer:myapp@localhost/myapp
        

    /__init__.py:main
        models.initialize_database(settings)
        

    /models/__init__.py
    
        import sqlassist
        def initialize_database(settings):
            engine_reader = sqlalchemy.engine_from_config(settings, prefix="sqlalchemy_reader.")
            sqlassist.init_engine('reader',engine_reader,default=True,reflect=myapp.models, use_zope=True)
            engine_writer = sqlalchemy.engine_from_config(settings, prefix="sqlalchemy_writer.")
            sqlassist.init_engine('writer',engine_writer,default=False,reflect=myapp.models, use_zope=True)
            
        from actual_models import *


    /models/actual_models.py
    
        from sqlassist import ReflectedTable

        class TestTable(ReflectedTable):
            __tablename__ = "test_table"
    
        
    in your handlers, you have this ( sqlalchemy is only imported to grab that error ):
    
    import myapp.lib.sqlassist as sqlassist
    import sqlalchemy
    
    def index(self):
        dbSession_reader = sqlassist.dbSession("reader")
        dbSession_writer = sqlassist.dbSession("writer")


        print dbSession_reader.query(models.actual_models.TestTable).all()

        try:
            #this should fail , assuming reader can't write
            dbTestTable= models.actual_models.TestTable()
            dbTestTable.name= 'Test Case 1'
            dbSession_reader.add(dbTestTable)
            $$COMMIT$$

        except sqlalchemy.exc.ProgrammingError:
            dbSession_reader.rollback()
            print "DENIED!"


        #but this should work , assuming writer can write
        dbTestTable= models.actual_models.TestTable()
        dbTestTable.name= 'Test Case 2'
        dbSession_writer.add(dbTestTable)
        $$COMMIT$$
        
    here's the caveats...
    $$COMMIT$$
        if you're using zope & transaction modules :
            - you need to call "transaction.commit" 
        if you're not using zope & transaction modules 
            - you need to call "dbession_writer.commit()" 
    Rollbacks
        you want to call rollback on the specific dbSessions to control what is in each one

    catching errors if you're trying to support both transaction.commit() and dbsession.commit()
        let's say you do this:
        
            try:
                dbSession_writer_1.add(object1)
                dbSession_writer_1.commit()
            except AssertionError , e:
                print "Should fail because zope wants this"

            # add to writer
            dbSession_writer_2.add(object2)

            # commit
            transaction.commit()
        
        in this event, both object1 and object2 will be committed by transaction.commit()
        you must explicitly call a rollback after the Assertion Error
        
    
        
	in case you want to use declared tables...
	
		in your models.py

			from sqlassist import DeclaredTable
			import sqlalchemy as sa
			
			class Group(DeclaredTable):
				__tablename__ = 'groups'
			
				id = sa.Column(sa.Integer, primary_key=True)
				name = sa.Column(sa.Unicode(255), nullable=False)
				description = sa.Column(sa.Text, nullable=False)

		and if you need a setup routine... 

			import sqlassist
			
			dbSession_writer = sqlassist.dbSession("writer")
		
			def callback():
				model = models.TestModel()
				dbSession_writer.add(model)
				dbSession_writer.flush()
				transaction.commit()
			
			sqlassist.initialize_sql('writer',callback)
		
		the initialize_sql wraps a bunch of code for you
	"""

import logging
log = logging.getLogger(__name__)

import types

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as sqlalchemy_orm


try:
   import transaction
   from zope.sqlalchemy import ZopeTransactionExtension 
except ImportError: 
   ZopeTransactionExtension= None
   transaction= None




__metadata= sqlalchemy.MetaData()

# define an engine registry
__engine_registry= { '!default':None , 'engines':{} }

# used for inheritance
DeclaredTable= declarative_base()


class EngineWrapper( object ):
    """wraps the SA engine object with mindless kruft"""

    def __init__( self, engine_name , sa_engine=None , sa_sessionmaker=None , sa_scoped_session=None ):
        log.debug("sqlassist#EngineWrapper.init()" )
        self.engine_name= engine_name
        self.sa_engine= sa_engine
        self.sa_sessionmaker= sa_sessionmaker
        self.sa_sessionmaker_params= None
        self.sa_scoped_session= sa_scoped_session
        
    def init_session( self , sa_sessionmaker_params ):
        if sa_sessionmaker_params:
            self.sa_sessionmaker_params= sa_sessionmaker_params
        self.sa_sessionmaker= sqlalchemy_orm.sessionmaker( **self.sa_sessionmaker_params )
        self.sa_scoped_session= sqlalchemy_orm.scoped_session( self.sa_sessionmaker )



def get_engine(name='!default'):
    """retrieves an engine from the registry"""
    log.debug("sqlassist#get_engine()" )
    try:
        if name == '!default': 
            name = __engine_registry['!default']
        return __engine_registry['engines'][name]
    except KeyError:
        raise RuntimeError("No engine '%s' was configured" % name)



def __dbSessionRemove( engine_name ):
    """
        Legacy Function.
        Probably not needed.
        ---
        removes a session from the stash. this is the heavy lifter.
    """
    _engine= get_engine(engine_name)
    _engine.sa_scoped_session.remove()


def dbSessionRemoveAll():
    """
        Legacy Function.
        Probably not needed.
        ---
        removes all our sessions from the stash.
        this was a cleanup activity once-upon-a-time
    """
    log.debug("sqlassist#dbSessionRemoveAll()" )
    for engine_name in __engine_registry['engines'].keys():
        __dbSessionRemove( engine_name )


def dbSessionInit():
    """
        Legacy Function.
        Probably not needed.
        ---
        removes all our sessions from the stash if they exist.  they shouldn't
    """
    log.debug("sqlassist#dbSessionInit()" )
    for engine_name in __engine_registry['engines'].keys():
        __dbSessionRemove( engine_type )




def init_engine( engine_name , sa_engine , default=False , reflect=False , use_zope=False , sa_sessionmaker_params=None ):
    """
    Creates new engines in the meta object and init the tables for each package
    """
    log.debug("sqlassist#init_engine()" )
    log.info("Initializing Engine : %s" % (engine_name) )
    
    # configure the engine around a wrapper
    wrapped = EngineWrapper( engine_name , sa_engine=sa_engine )
    
    # these are some defaults that i once used for writers
    # loggers would autocommit as true
    # not sure this is needed with zope
    if sa_sessionmaker_params is None:
        sa_sessionmaker_params= {}
    _sa_sessionmaker_params= { 'autoflush':True, 'autocommit':False , 'bind':sa_engine }
    for i in _sa_sessionmaker_params.keys():
        if i not in sa_sessionmaker_params:
            sa_sessionmaker_params[i]= _sa_sessionmaker_params[i]
    
    if use_zope:
        if ZopeTransactionExtension is None:
            raise ImportError('ZopeTransactionExtension was not imported earlier')
        if 'extension' in sa_sessionmaker_params:
            raise ValueError('I raise an error when you call init_engine() with `use_zope=True` and an `extension` in sa_sessionmaker_params. Sorry.')
        sa_sessionmaker_params['extension']= ZopeTransactionExtension()
        
    wrapped.init_session(sa_sessionmaker_params)
    
    # stash the wrapper
    __engine_registry['engines'][engine_name]= wrapped
    if default:
        __engine_registry['default']= engine_name
        
        
    # finally, reflect if needed
    if reflect:
        reflect_tables( reflect , primary=default , metadata=__metadata , engine_name=engine_name , sa_engine=sa_engine )
    


def dbSession( engine_name ):
    """dbSession(engine_name): wraps get_engine and returns the sa_scoped_session"""
    log.debug("sqlassist#dbSession(%s)" % engine_name )
    session= get_engine(engine_name).sa_scoped_session
    return session



class UtilityObject(object):
    __table_pkey__= None

    def get__by__id( self, dbSession, id , id_column='id' ):
        """gets an item by an id column named 'id'.  id column can be overriden"""
        if not hasattr( self.__class__ , id_column ) and hasattr( self, '__table_pkey__' ) :
            id_column= self.__table_pkey__
        id_col= getattr( self.__class__ , id_column )
        if type(id) == type([]):
            return dbSession.query(self.__class__).filter( id_col.in_(id) ).all()
        else :
            id_dict= { id_column : id }
            return dbSession.query(self.__class__).filter_by( **id_dict ).first()


    def get__by__column__lower( self, dbSession, column , search , allow_many=False ):
        """gets items from the database based on a lowercase version of the column. useful for situations where you have a function index on a table, such as indexing on the lower version of an email addresses."""
        items= dbSession.query(self.__class__).filter( sqlalchemy.sql.func.lower( getattr( self.__class__ , column ) ) == search.lower() ).all()
        if items:
            if not allow_many:
                if len(items) > 1 :
                    raise ValueError("get__by__column__lower should return 1 and only 1 item")
                elif len(items) == 1:
                    return items[0]
            else:
                return items
        return None


    def get__by__column__similar( self, dbSession , column , seed , prefix_only=True):
        """seaches for a name column entry with the submitted seed prefix"""
        search_template= "%s%%"
        if not prefix_only:
            search_template= "%%%s%%"
        return dbSession.query(self.__class__).filter( (getattr( self.__class__ , column)).ilike( search_template % seed ) ).order_by( getattr( self.__class__ , column ) ).all()


    def get__by__column__exact_then_ilike( self, dbSession, column, seed ):
        """ seaches for an exact, then case-insensitive version of the name column"""
        item= dbSession.query(self.__class__).filter( getattr( self.__class__ , column ) == seed ).first()
        if not item:
            item= dbSession.query(self.__class__).filter( getattr( self.__class__ , column ).ilike(seed) ).first()
        return item




class ReflectedTable(UtilityObject): 
    """Base class for database objects that are mapped to tables by reflection.
       Have your various model classes inherit from this class.  If class.__tablename__ is defined, it will reflect

       Example:
          class Useraccount(ReflectedTable):
              __tablename__ = "useraccount"
    """ 
    __tablename__ = None
    __sa_stash__ = {}


def reflect_tables( app_model , primary=False , metadata=None , sa_engine=None , engine_name=None ):
    """this reflects tables via sqlalchemy.  recursively goes through the application's model package looking for classes that inherit from ReflectedTable
    
        app_model- the package you want to reflect.  pass in a package, not a string
        
        Good:
            reflect_tables( myapp.models , primary=True )
        
        Bad - this won't work at all:
            reflect_tables( 'myapp.models' , primary=True )
        
    """
    log.debug("sqlassist#reflect_tables(%s)" % app_model )
    to_reflect = []
    for content in dir( app_model ):
        module = getattr( app_model , content )
        if not isinstance( module , types.ModuleType ):
            continue
        for module_element in dir( module ):
            module_element = getattr( module, module_element )
            if not isinstance( module_element , types.TypeType ):
                continue
            if issubclass( module_element , ReflectedTable ):
                to_reflect.append( module_element )
    for _class in to_reflect: 
        table_name = _class.__tablename__
        if table_name:
            log.info("Reflecting : %s (table: %s)" % (_class , table_name) )

            # turn off SQL Query logging in sqlAlchemey for a moment , it's just makes a mess of things
            _level= logging.getLogger('sqlalchemy.engine').getEffectiveLevel()
            if _level < logging.WARN :
                logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
            
            table= sqlalchemy.Table( table_name, metadata, autoload=True , autoload_with=sa_engine )
            _class.__sa_stash__[engine_name]= table
            if primary:
                sqlalchemy_orm.mapper( _class , table ) 
            else:
                sqlalchemy_orm.mapper( _class , table , non_primary=True ) 

            # return logging to it's former state
            logging.getLogger('sqlalchemy.engine').setLevel(_level)
            

def initialize_sql(engine_name,population_callback):
    _dbSession= dbSession(engine_name)
    _sa_engine= get_engine(engine_name).sa_engine
    _dbSession.configure( bind = _sa_engine  )
    DeclaredTable.metadata.bind = _sa_engine
    DeclaredTable.metadata.create_all(_sa_engine)
    try:
        population_callback()
    except IntegrityError:
        transaction.abort()

