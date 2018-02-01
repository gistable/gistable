import os

'''
.ssh/config (windows,for local git server):
Host host100
        Hostname 192.168.1.100
        User git
        IdentityFile C:/Users/admin/.ssh/id_rsa_gitBackup_host100
		
repo example:
	/home/git/test1.git
'''	
def localGitBackup(hostName,dirList):
	for dirName in dirList:
		print dirName," : ",
		if os.path.exists(dirName):		
			strCmd = "cd %s && git pull && cd .." % dirName		
			os.system(strCmd)
		else:		
			strCmd = "git clone %s:%s.git " % (hostName,dirName)
			os.system(strCmd)

'''
.ssh/config (windows,for github):
Host github
        Hostname github.com
        User git
        IdentityFile C:/Users/admin/.ssh/id_rsa_github
'''			
#for github repos
def githubReposBackup(hostName,userName,repoList):
	for repo in repoList:
		print repo," : ",
		if os.path.exists(repo):		
			strCmd = "cd %s && git pull && cd .." % repo		
			os.system(strCmd)
		else:		
			strCmd = "git clone %s:%s/%s.git " % (hostName,userName,repo)
			os.system(strCmd)

'''
.ssh/config (windows,for github):
Host gist
        Hostname gist.github.com
        User git
        IdentityFile C:/Users/admin/.ssh/id_rsa_github_gist
'''
#for gist 
def githubGistsBackup(host,gistList):
	for gist in gistList:
		print gist," : ",
		if os.path.exists(gist):		
			strCmd = "cd %s && git pull && cd .." % gist		
			os.system(strCmd)
		else:		
			strCmd = "git clone %s:%s.git " % (host,gist)
			os.system(strCmd)		
	
if __name__ == "__main__":
	host_local = "host100"
	host_github = "github"
	host_gist = "gist"
	
	userName_github = "mike-zhang"
	
	dirList_local = [
		'test1',
		'test2'
	]
	
	repoList_github = [
		'cppCallLua',
		'testCodes'
	]
	
	gistList_github = [
		'4166192',
		'4084385'
	]	
	
	localGitBackup(host_local,dirList_local)
	githubReposBackup(host_github,userName_github,repoList_github)	
	githubGistsBackup(host_gist,gistList_github)
