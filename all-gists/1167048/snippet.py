
from fabric.api import settings, roles, env, run, sudo, cd
from fabric.decorators import task
from fabric import tasks
from fabric.contrib.project import rsync_project


env.roledefs = {
  'dev': [
    'vagrant@127.0.0.1:2222'
  ],
  'prod': [
    'www1', 
    'www2', 
    'www3'
  ],
}


class DemoDeployment(tasks.Task):

  name = 'deploy'

  def run(self):
    self.refresh_code()    
    run('coffee -c /srv/fabric-demo/src/js/')
    sudo('service nginx reload')    

  def refresh_code(self):
    rsync_project(
      remote_dir = '/srv/fabric-demo',
      local_dir = './',
      delete = True,
      exclude = ['*.pyc', 'fabfile.py', '.vagrant', 'Vagrantfile'],
    )


class DemoProductionDeployment(DemoDeployment):

  name = 'production_deploy'
  
  def refresh_code(self):
    with cd('/srv/fabric-demo/'):
      run('git checkout -- .')
      run('git pull')


@task
@roles('dev')
def deploy():
  env.key_filename = '/Library/Ruby/Gems/1.8/gems/vagrant-0.8.2/keys/vagrant'
  t = DemoDeployment()
  t.run()


@task
@roles('prod')
def production_deploy():
  t = DemoProductionDeployment()
  t.run()
