# -*- coding: utf-8 -*-
import json
import os

from flask import Flask, request, g, session, redirect, url_for, Response
from flask import render_template_string, render_template

import requests
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.environ["DATABASE_URL"]
DATABASE_URL = DATABASE_URL.replace("postgresql", "postgresql+psycopg2")
SECRET_KEY = os.environ["APP_SECRET_KEY"]
DEBUG = False

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URL'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(200), nullable=False)
    password = Column(String(300), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password


class Command(Base):
    __tablename__ = 'command'

    id = Column(Integer, primary_key=True)
    email = Column(String(200), nullable=False)
    commands = Column(Text(), nullable=True)

    def __init__(self, email, commands):
        self.email = email
        self.commands = commands


@app.teardown_request
def teardown_request(exception):
    if exception:
        db_session.rollback()
        db_session.remove()
    db_session.remove()


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route('/check-user', methods=['POST'])
def check_user():
    if request.method == 'POST':
        email = request.json['email']
        count = User.query.filter_by(email=email).count()

        json_res = {}
        if count == 1:
            json_res['exists'] = True
        else:
            json_res['exists'] = False
        json_res = json.dumps(json_res)
        return Response(json_res, status=200)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return redirect('https://orkohunter.net/keep')
    elif request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        user = User(email, password)
        db_session.add(user)
        db_session.commit()
        return Response(status=200)


@app.route('/push', methods=['POST'])
def push():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        commands = request.json['commands']
        user = User.query.filter_by(email=email).first()
        if user.password == password:
            command = Command.query.filter_by(email=email).first()
            if command is None:
                command = Command(email, commands)
                db_session.add(command)
            command.commands = commands
            db_session.commit()
            return Response(status=200)
        else:
            return Response(status=403)


@app.route('/pull', methods=['POST'])
def pull():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        user = User.query.filter_by(email=email).first()
        if user.password == password:
            command = Command.query.filter_by(email=email).first()
            commands = None
            if command is not None:
                commands = command.commands
            json_res = {
                'commands': commands
            }
            json_res = json.dumps(json_res)
            return Response(json_res, status=200)
        else:
            return Response(status=403)

if __name__ == '__main__':
    #init_db()
    app.run(debug=True)
