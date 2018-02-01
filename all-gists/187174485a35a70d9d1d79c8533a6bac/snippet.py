#!/usr/bin/env python3
import sys
import subprocess as sp
from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser


def ssh(host, cmd):
    return sp.check_output(['ssh', host, cmd]).strip().decode()


def rsync(*args):
    sp.run(['rsync', *args], check=True)


def backup(*, sources, exclude, host, destination, logdir, dry=False, list_=False):
    sources = [p for patt in sources for p in Path.home().glob(patt)]
    exclude = ['--exclude=' + patt for patt in exclude]
    if list_:
        rsync(
            *'--dry-run -i -az --stats'.split(),
            *exclude,
            *sources,
            '/tmp/backup_asodif'
        )
        return
    date = ssh(host, "date +'%Y-%m-%d-%H%M%S'")
    print('Old:', ssh(host, f'readlink {destination}/Latest'))
    print('New:', date)
    location = f'{destination}/{date}.inProgress'
    if dry:
        rsync(
            *'--dry-run -i -az --stats --link-dest=../Latest'.split(),
            *exclude,
            *sources,
            f'{host}:{location}/'
        )
        return
    ssh(host, f'mkdir {location}')
    logdir.mkdir(exist_ok=True)
    extra_args = []
    if sys.stdout.isatty():
        extra_args.append('--info=progress2')
    rsync(
        *f'--log-file={logdir}/{date}.log -az --stats --link-dest=../Latest'.split(),
        *extra_args,
        *exclude,
        *sources,
        f'{host}:{location}/'
    )
    ssh(host, f'mv {location} {destination}/{date} && ln -fns {date} {destination}/Latest')


def get_cli():
    parser = ArgumentParser()
    parser.add_argument('--dry', action='store_true')
    parser.add_argument('-l', '--list', dest='list_', action='store_true')
    return vars(parser.parse_args())


def get_conf():
    config = ConfigParser()
    config.read(Path.home()/'.config/backup/config.ini')
    conf = dict(config['backup'])
    conf['logdir'] = Path(conf['logdir']).expanduser()
    conf['sources'] = conf['sources'].split(',')
    conf['exclude'] = conf['exclude'].split(',')
    return conf


if __name__ == '__main__':
    backup(**get_conf(), **get_cli())
