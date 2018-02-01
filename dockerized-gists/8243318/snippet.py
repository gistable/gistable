"""
Simple web server that listens for Github webhooks to implement push-to-deploy
with Pelican static sites

Settings are loaded from a json file except for SECRET which should be an
environment variable

Example `deployer.json`

{
  "repos": {
    "mysite": {
      "root": "/path/to/repo",
      "remote": "origin",
      "output": "/srv/www/{branch}"
    }
  },
  "port": 5000
}

Run it

$ SECRET=thisisasecret python ./pelican_deployer.py deployer.json

Add http://<deployer_host>/mysite/thisisasecret as a webhook url and you're done
"""
import logging
import os
import subprocess
import sys

from flask import Flask, json, jsonify, request

app = Flask(__name__)


def sh(cmd, **kwargs):
  cmd = cmd.format(**kwargs)
  output = subprocess.check_output(
    cmd,
    stderr=subprocess.STDOUT,
    shell=True,
  )
  app.logger.info('\n' + cmd)
  app.logger.info('\n'.join([' > ' + l for l in output.split('\n')]))
  

@app.route('/<repo_id>/{}'.format(os.environ['SECRET']), methods=['POST'])
def deploy(repo_id):
  payload = json.loads(request.form['payload'])
  branch = payload.get('ref').split('/')[2]
  repo = app.config['repos'][repo_id]
  os.chdir(repo['root'])
  sh(
    'git checkout {branch}',
    branch=branch,
  )
  sh(
    'git pull --ff-only {remote} {branch}',
    remote=repo.get('remote', 'origin'),
    branch=branch,
  )
  sh(
    'pelican -d -o {output} content',
    output=repo['output'].format(branch=branch, **payload),
  )
  return jsonify(dict(ok=True))


if __name__ == '__main__':
  with open(sys.argv[1]) as f:
    app.config.update(**json.load(f))
  app.logger.addHandler(logging.StreamHandler())
  app.logger.setLevel(logging.INFO)
  app.run(port=int(os.environ.get('PORT', 5000)))

