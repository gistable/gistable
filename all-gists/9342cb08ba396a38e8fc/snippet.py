#!/usr/bin/env python3


def options(opts):
	opts.load('compiler_cxx')

def configure(conf):
	conf.load('compiler_cxx')
	conf.check(features='cxx cxxprogram', cxxflags=['-std=c++14', '-Wall', '-Wextra', '-O3', '-pedantic', '-pipe'], uselib_store='M')

def build(buld):
	buld(features='cxx cxxstlib', source=buld.path.ant_glob('src/**/*.cpp'), target='cpponfig', use='M')
