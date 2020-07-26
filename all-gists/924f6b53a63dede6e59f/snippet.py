#
# Extract files from Bare git-annex repositories without git-annex
# Supports version v6
#
# See internals: http://git-annex.branchable.com/internals/
#
# Modified: added non-bare repos, added tar file (of symlinks) output for use with archivemount
#
# TODO: improve output
# TODO: use cat-files instead of archive
# TODO: export to tar WITH relative links
#
# Emanuele Ruffaldi (C) 2016
import sys,argparse,os,subprocess
import md5,tarfile,cStringIO,hashlib,struct

def gitgetpathinfo(branch,path,recurse=False):
	"""uses ls-tree to extract information about a path in the branch or in general tree-ish"""
	if recurse:
		r = "-r"
	else:
		r = ""
	w = subprocess.check_output(["git", "ls-tree",r,branch,"--",path])
	return [pa.split("\t") for pa in w.split("\n") if pa != ""] # meta TAB filename ==> meta is: ?? SPACE type 

def tarextraclink(content):
	"""extracts the path of a link in a Tar expressed by content"""
	t = tarfile.open(mode="r",fileobj=cStringIO.StringIO(content))
	ti = t.getmembers()[0]
	return ti.linkname

def gitgetfile(branch,path):
	"""uses archive for extracing the path. This is better than the git show solution because it deals with diff automatically. But does not work with symbolic links"""
	xpath,n = os.path.split(path)
	xx = "git archive --format=tar --prefix= \"%s:%s\" \"%s\" | tar -xO \"%s\"" % (branch,xpath,n,n)
	return subprocess.check_output(xx,shell=True)

def gitgetfile_tar(branch,path):
	"""returns the content of a file in tar format"""
	try:
		xpath,n = os.path.split(path)
		xx = "git archive --format=tar --prefix= \"%s:%s\" \"%s\"" % (branch,xpath,n)
		return subprocess.check_output(xx,shell=True)
	except:
		return None

def gitgetfile_show(branch,path):
	"""retrieve path content: first getting the hash and then the content via git show"""
	found = gitgetpathinfo(branch,path)
	if len(found) == 1:
		return subprocess.check_output(["git", "show",found[0][0].split(" ")[2]])
	else:
		return None

def annexgetremotes(useshow):
	"""list of remotes AKA uuid.log"""
	if useshow:
		return gitgetfile_show("git-annex","uuid.log")
	else:  # slow with bare
		return gitgetfile("git-annex","uuid.log")

#https://gist.github.com/giomasce/a7802bda1417521c5b30
def hashdirlower(key):
    hasher = hashlib.md5()
    hasher.update(key)
    digest = hasher.hexdigest()
    return "%s/%s/" % (digest[:3], digest[3:6])

#https://gist.github.com/giomasce/a7802bda1417521c5b30
def hashdirmixed(key):
    hasher = hashlib.md5()
    hasher.update(key)
    digest = hasher.digest()
    first_word = struct.unpack('<I', digest[:4])[0]
    nums = [first_word >> (6 * x) & 31 for x in xrange(4)]
    letters = ["0123456789zqjxkmvwgpfZQJXKMVWGPF"[i] for i in nums]
    return "%s%s/%s%s/" % (letters[1], letters[0], letters[3], letters[2])

def annexwhereis_bare(key):
	"""returns the location of the key object of git-annex"""
	#hashdirlower is used for bare git repositories, the git-annex branch, and on special remotes as well.
	#m = md5.new()
	#m.update(key)
	#h = m.hexdigest()
	#pre = h[0:3]
	#post = h[3:6]
	#print key,pre,post
	papa = hashdirlower(key)
	return gitgetfile("git-annex",os.path.join(papa,key+".log")),os.path.join("annex","objects",papa,key,key)

def annexwhereis(key):
	"""returns the location of the key object of git-annex"""
	#non bare uses hashdirmixed
	#It takes the md5sum of the key, but rather than a string, represents it as 4 32bit words. Only the first word is used. It is converted into a string by the same mechanism that would be used to encode a normal md5sum value into a string, but where that would normally encode the bits using the 16 characters 0-9a-f, this instead uses the 32 characters "0123456789zqjxkmvwgpfZQJXKMVWGPF". The first 2 letters of the resulting string are the first directory, and the second 2 are the second directory.
	papaM = hashdirmixed(key)
	papaL = hashdirlower(key)
	return gitgetfile("git-annex",os.path.join(papaL,key+".log")),os.path.join("annex","objects",papaM,key,key)

def checkbare(args):
	"""checks if the repo is a bare"""
	gitdir = os.path.join(args.annex,".git")
	if os.path.isdir(gitdir):
		if not os.path.isdir(os.path.join(gitdir,"annex")):
			return None
		else:
			return False,gitdir
	elif os.path.isdir(os.path.join(args.annex,"annex")):
		gitdir = args.annex
		return True,gitdir
	else:
		return None

def main():

	parser = argparse.ArgumentParser(description='Retrieve file from git-annex, even barebone')
	parser.add_argument('--annex', help="path to annex repository",default=".")
	parser.add_argument('path', help="file to be looked at",nargs="*")
	parser.add_argument('--all', help="list all",action="store_true")
	parser.add_argument('--verbose', help="verbose dump",action="store_true")
	parser.add_argument('--tar', help="produces a tar file with given path cotaining the symbolic links")
	parser.add_argument('--abs',help="makes abs files",action="store_true")

	args = parser.parse_args()

	# check if bare repository
	isbare = checkbare(args)
	if isbare is None:
		print "not a git-annex repisitory"
	isbare,gitdir = isbare
	print "isbare?",isbare,gitdir

	if not isbare:
		workdir = args.annex
	else:
		workdir = None

	os.environ["GIT_DIR"] = gitdir
	print "list annexes\n",annexgetremotes(useshow=False)

	if args.tar:
		ot = tarfile.open(args.tar,"w")

	if args.all:
		args.path = [x[1] for x in gitgetpathinfo("main","",recurse=True)]

	for p in args.path:
		# we cannot use 
		ww = gitgetfile_tar("main",p) # tarred 1 file
		if ww is None:
			print "not found",p
			continue
		link = tarextraclink(ww) # extract the link from the single file
		if args.verbose:
			print "aslink",link
		#w = gitgetfile("main",p) -- not working using tar because it is a link
		#ref = gitgetfile_show("main",p) -- not working in theory
		ref = link
		if ref == "":
			print "not found",p
		else:
			key = os.path.split(ref)[1] # the link contains the annex key
			if args.verbose:
				print "key is",key
			if isbare:
				locations,path = annexwhereis_bare(key) # extract 
			else:
				locations,path = annexwhereis(key)
			path = os.path.join(gitdir,path)

			if args.verbose:
				print p,"located in\n",locations
			if not os.path.isfile(path):
				if not isbare:
					if os.path.isfile(path+".map"):
						mpath = os.path.join(workdir,open(path+".map","r").read().strip())
						if os.path.isfile(mpath):
							path = mpath
						else:
							print "mapped file not found",mpath," for ",path # or direct mode not supported
							path = None
					else:
						print "non bare file not found",path # or direct mode not supported
						path = None
				else:
					print "file not found",path # or direct mode not supported
					path = None
			if path is not None:
				ss = os.stat(path)
				print path,ss
				ti = tarfile.TarInfo(p)
				ti.size = 0 # zero for links: ss.st_size
				ti.mode = ss.st_mode
				ti.mtime = ss.st_mtime
				ti.type = tarfile.SYMTYPE
				ti.uid = ss.st_uid
				ti.gid = ss.st_gid
				if args.abs:
					ti.linkname = os.path.abspath(path)
				else:
					ti.linkname = path
				ot.addfile(ti)

if __name__ == '__main__':
	main()