# pip install PyGithub
from github import Github

g = Github(G_USER, G_PASS)

for gist in g.get_user().get_gists():
  gist.delete()
