"""
Gets the name of the active Git branch as a string.
Depends on GitPython

pip install GitPython
"""
from git import Repo

repo = Repo('/path/to/your/repo')
branch = repo.active_branch
print branch.name

"""
Example usage from my local Django settings:

try:
    # use the develop database if we are using develop
    import os
    from git import Repo

    repo = Repo(os.getcwd())
    branch = repo.active_branch
    branch = branch.name
    if branch == 'develop':
        DATABASES['default']['NAME'] = 'myproject__develop'
except ImportError:
    pass
"""