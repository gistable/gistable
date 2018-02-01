import git

def clone(cls, directory, url, depth=3):
    return git.Repo.clone_from(url, directory, depth=depth)

