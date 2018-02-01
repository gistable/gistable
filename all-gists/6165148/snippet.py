#!/usr/bin/env python3
# @python3
# @author Kalman Olah <hello@kalmanolah.net>
"""A hastebin CLI tool."""
import click
import json
import requests
import subprocess
import sys

__VERSION__ = '0.0.2'
__BASE_URL__ = 'http://hastebin.com'


def show_version(ctx, param, value):
    """Print version information and exit."""
    if not value:
        return

    click.echo('haste %s' % __VERSION__)
    ctx.exit()


@click.command()
@click.option('--clip', '-c', is_flag=True, help='Use clipboard input (xsel).')
@click.option('--version', '-v', is_flag=True, is_eager=True,
              help='Print version information and exit.', expose_value=False,
              callback=show_version)
@click.argument('file', type=click.File('r'), required=False)
@click.pass_context
def haste(ctx, clip, file):
    """A hastebin CLI tool."""
    input = get_input(clip, file)
    if not input:
        click.echo('You need input!')
        ctx.exit()

    r = requests.post('%s/documents' % __BASE_URL__, input.encode('utf8'))
    url = '%s/%s' % (__BASE_URL__, json.loads(r.content.decode())['key'])

    click.echo(click.style(url, fg='green'))
    copy_to_clipboard(url)


def copy_to_clipboard(str):
    """Copy a string to the clipboard."""
    p = subprocess.Popen(['xsel', '-ib'], stdin=subprocess.PIPE)
    p.communicate(input=bytes(str, 'UTF-8'))


def get_input(clip, file):
    """Retrieve the correct input."""
    if file:
        input = file.read()
    elif clip:
        input = subprocess.check_output(['xsel', '-ob']).decode()
    elif not sys.stdin.isatty():
        input = click.get_text_stream('stdin').read()
    else:
        input = click.prompt('Provide some input')

    return input.strip()


if __name__ == '__main__':
    haste(obj={}, auto_envvar_prefix='HASTE')