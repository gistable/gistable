from fabric.api import local
import pip

def freeze ():
    local("pip freeze > requirements.txt")
    local("git add requirements.txt")
    local("git commit -v")

def upgrade ():
    for dist in pip.get_installed_distributions():
        local("pip install --upgrade {0}".format(dist.project_name))