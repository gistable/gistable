# -*- coding: utf-8 -*-
import os
import click


class HTTPClient(object):
    def __init__(self, token=None, debug=False, base_url=''):
        self._token = token
        self._debug = debug
        self._base_url = base_url

    def get(self, path):
        print('httpclient get {}'.format(path))

    def post(self):
        print('httpclient post')

    def put(self):
        print('httpclient put')

    def delete(self):
        print('httpclient delete')


class ProjectManager():
    def __init__(self, httpclient):
        self.httpclient = httpclient

    def list(self):
        print('Going to list projects')
        self.httpclient.get('/projects')

    def get(self):
        print('Going to get project')
        self.httpclient.get('/project/<id>')


class SubnetManager():
    def __init__(self, httpclient):
        self.httpclient = httpclient

    def list(self):
        print('Going to list subnets')
        self.httpclient.get('/subnets')

    def get(self):
        print('Going to get subnet')
        self.httpclient.get('/subnet/<id>')


# Base group
@click.group()
@click.option('--token', envvar='SELVPCTOKEN', default='')
@click.option('--debug/--no-debug', default=False)
@click.option('--base_url', envvar='SELVPCURL', default='')
@click.pass_context
def cli(ctx, token, debug, base_url):
    ctx.obj = HTTPClient(token, debug, base_url)


# Group for projects ops
@cli.group()
@click.pass_context
def projects(ctx):
    httpclient = ctx.obj
    ctx.obj = ProjectManager(httpclient)


# Group for subnets ops
@cli.group()
@click.pass_context
def subnets(ctx):
    httpclient = ctx.obj
    ctx.obj = SubnetManager(httpclient)


# Common list command
@click.command()
@click.pass_context
def list(ctx):
    manager = ctx.obj
    manager.list()


# # Common get command
@click.command()
@click.pass_context
def get(ctx):
    manager = ctx.obj
    manager.get()

# Connect each command to each group manually
subnets.add_command(list)
projects.add_command(list)
subnets.add_command(get)
projects.add_command(get)

if __name__ == '__main__':
    cli()
