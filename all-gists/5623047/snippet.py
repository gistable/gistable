# encoding=utf8

import os

import cuisine

from fabric.api import run, sudo, cd, task, local

from fabtools.vagrant import vagrant

# curl -XPUT -i -H 'content-type: application/json' http://localhost:8098/yz/index/name_of_index
# curl -XGET -i -H 'content-type: text/plain' -X PUT 'http://localhost:8098/buckets/name_of_bucket/keys/name' -d "Ryan Zezeski"
# curl -XGET -i 'http://localhost:8098/search/name_of_index?q=text:Ryan'

def packages_install(packages):
    """
    >>> packages_install('gcc gcc-c++ make openssl-devel ncurses-devel')
    """
    for package in packages.split():
        package_install(package)

@task
def setup_yokozuna():

    packages_install('java-1.7.0-openjdk-devel')

    cuisine.dir_ensure('src')

    with cd('src'):
        filename = 'riak-yokozuna-0.6.0-src.tar.gz'

        if not os.path.exists(filename):
            local('curl -O http://data.riakcs.net:8080/yokozuna/riak-yokozuna-0.6.0-src.tar.gz')

        cuisine.file_upload(filename, filename)
        run('tar zxvf riak-yokozuna-0.6.0-src.tar.gz')

        with cd('riak-yokozuna-0.6.0-src'):
            run('make')
            run('make stage')

            run("sed -e '/{yokozuna,/,/]}/{s/{enabled, false}/{enabled, true}/;}' -i.back rel/riak/etc/app.config")

            # run("for d in dev/dev*; do sed -e '/{yokozuna,/,/]}/{s/{enabled, false}/{enabled, true}/;}' -i.back $d/etc/app.config; done")
            # run('for d in dev/dev*; do $d/bin/riak start; done')
            # run('for d in dev/dev*; do $d/bin/riak ping; done')

@task
def setup_erlang(version='R15B03'):

    packages_install('gcc gcc-c++ make openssl-devel ncurses-devel')

    cuisine.dir_ensure('src')

    with cd('src'):
        upload_erlang(version)
        run('tar xvfz otp_src_{0}.tar.gz'.format(version))

        with cd('otp_src_{0}'.format(version)):

            run('./configure --prefix=/opt/erlang/{0} \
                             --enable-threads \
                             --enable-smp-support \
                             --enable-halfword-emulator \
                             --enable-m64-build \
                             --disable-native-libs \
                             --disable-sctp \
                             --enable-kernel-poll \
                             --disable-hipe \
                             --without-javac'.format(version))
            run('make')
            sudo('make install')
    run("echo 'export PATH=/opt/erlang/R15B03/bin:$PATH' >> .bashrc")
    run('source .bashrc')

def package_install(package):
    cuisine.package_install_yum(package)

def upload_erlang(version):
    filename = 'otp_src_{0}.tar.gz'.format(version)
    if not os.path.exists(filename):
        local('curl -O http://download.basho.co.jp.cs-ap-e1.ycloud.jp/download/otp_src_{0}.tar.gz'.format(version))

    cuisine.file_upload(filename, filename)

