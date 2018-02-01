from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
try:
    app.config.from_object("config")
except:
    pass

if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    from sqlalchemy import event
    event.listen(sensing_db.engine, 'connect', _fk_pragma_on_connect)


