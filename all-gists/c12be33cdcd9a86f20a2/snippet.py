from flask.ext.sqlalchemy import SQLAlchemy

def get_model(self, name):
    return self.Model._decl_class_registry.get(name, None)
SQLAlchemy.get_model = get_model

def get_model_by_tablename(self, tablename):
  for c in self.Model._decl_class_registry.values():
    if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
      return c
SQLAlchemy.get_model_by_tablename = get_model_by_tablename
      
db = SQLAlchemy(app)