import json
import os
from sh import karma
from sh import uglifyjs
from sh import jshint

top = '.'
out = 'build'

def options(ctx):
  ctx.load('pebble_sdk')

def configure(ctx):
  ctx.load('pebble_sdk')

def distclean(ctx):
  ctx.load('pebble_sdk')
  try:
    os.remove('../src/js/pebble-js-app.js')
    os.remove('../src/js/src/appinfo.js')
    os.remove('../src/generated/appinfo.h')
  except OSError as e:
    pass

def build(ctx):
  ctx.load('pebble_sdk')

  js_sources = [
    '../src/js/src/lib/http.js',
    '../src/js/src/lib/pebble-ga.js',
    '../src/js/src/appinfo.js',
    '../src/js/src/main.js'
  ]
  built_js = '../src/js/pebble-js-app.js'

  # Generate appinfo.js
  ctx(rule=generate_appinfo_js, source='../appinfo.json', target='../src/js/src/appinfo.js')

  # Generate appinfo.h
  ctx(rule=generate_appinfo_c, source='../appinfo.json', target='../src/generated/appinfo.h')

  # Run jshint on all the JavaScript files
  ctx(rule=js_jshint, source=js_sources)

  # Run the suite of JS tests.
  ctx(rule=js_karma)

  # Combine the source JS files into a single JS file.
  ctx(rule=concatenate_js, source=' '.join(js_sources), target=built_js)

  # Build and bundle the Pebble app.
  ctx.pbl_program(source=ctx.path.ant_glob('src/**/*.c'), target='pebble-app.elf')
  ctx.pbl_bundle(elf='pebble-app.elf', js=built_js)

def generate_appinfo_c(task):
  ext_out = '.c'
  src = task.inputs[0].abspath()
  target = task.outputs[0].abspath()
  appinfo = json.load(open(src))

  f = open(target, 'w')
  f.write('#pragma once\n\n')
  f.write('#define VERSION_LABEL "{0}"\n'.format(appinfo["versionLabel"]))
  f.write('#define VERSION_CODE {0}\n'.format(appinfo["versionCode"]))
  f.write('#define UUID "{0}"\n'.format(appinfo["uuid"]))
  for key in appinfo['appKeys']:
    f.write('#define APP_KEY_{0} {1}\n'.format(key.upper(), appinfo['appKeys'][key]))
  f.close()

def generate_appinfo_js(task):
  src = task.inputs[0].abspath()
  target = task.outputs[0].abspath()
  data = open(src).read().strip()

  f = open(target, 'w')
  f.write('/* exported AppInfo */\n\n')
  f.write('var AppInfo = ')
  f.write(data)
  f.write(';')
  f.close()

def concatenate_js(task):
  inputs = (input.abspath() for input in task.inputs)
  uglifyjs(*inputs, o=task.outputs[0].abspath())

def js_jshint(task):
  inputs = (input.abspath() for input in task.inputs)
  jshint(*inputs, config="../pebble-jshintrc")

def js_karma(task):
  ext_out = '.js'
  karma("start", single_run=True, reporters="dots")