from distutils.spawn import find_executable
import os
import re
import sys
import subprocess
import zipfile
import tempfile
import shutil


def main():
	argvs = sys.argv
	if (len(argvs) != 3):
		print("invalid argument length.")
		print("usage: python {0} module_name version".format(os.path.basename(__file__)))
		quit()

	play_service_name = argvs[1]
	version = argvs[2]

	root = sdk_root()
	print("Android SDK path: " + root)

	repo_path = google_repository(root)

	try:
		temp_dir = tempfile.mkdtemp()
		# check prefix
		if (not play_service_name.startswith("play-services-")):
			play_service_name = "play-services-" + play_service_name
		# unzip aar
		aar = os.path.join(repo_path, play_service_name, version, "{0}-{1}.aar".format(play_service_name, version))
		if not os.path.exists(aar):
			raise IOError("{0} not found.".format(os.path.basename(aar)))
		target_name = "{0}-{1}".format(play_service_name, version)
		unzip(aar, os.path.join(temp_dir, target_name))
		unzipped = os.path.join(temp_dir, target_name)
		# make directory
		os.mkdir(os.path.join(unzipped, "src"))
		os.mkdir(os.path.join(unzipped, "libs"))
		# move jar to libs directory
		shutil.move(os.path.join(unzipped, "classes.jar"), os.path.join(unzipped, "libs"))
		# create project.properties
		pp = open(os.path.join(unzipped, "project.properties"), 'w')
		pp.write("android.library=true")
		# remove unnecessary file
		os.remove(os.path.join(unzipped, "R.txt"))
		# move created library to working directory
		if os.path.exists(target_name):
			shutil.rmtree(target_name)
		shutil.move(unzipped, target_name)

		print("Create play service library: " + os.path.abspath(target_name))
	except Exception as e:
		print("Error: " + str(e))

	os.rmdir(temp_dir)


# get sdk root path
def sdk_root():
	uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
	try:
		executable = find_executable("adb")
		return uppath(os.path.abspath(executable), 2)
	except subprocess.CalledProcessError:
		print("Android sdk not found. Please input android sdk location:")
		input_line = os.path.abspath(raw_input())
		adb = os.path.join(input_line, "platform-tools" , "adb")
		if os.path.exists(adb):
			return input_line
		else:
			sdk_root()


# Check and install Google Repository
def google_repository(sdk_root):
	repo_path = os.path.join(sdk_root, "extras", "google", "m2repository", "com", "google", "android", "gms")
	if os.path.exists(repo_path):
		return repo_path
	else:
		# If Google Repository is not installed, install it automatically.
		print ("Android Support Repository not installed.")
		print ("Retrieving available package list...")
		p_list = subprocess.Popen(["android", "list", "sdk", "--all"], shell=False, stdout=subprocess.PIPE)
		grep = subprocess.Popen(["grep \"Google Repository\""], shell=True, stdin=p_list.stdout, stdout=subprocess.PIPE)
		p_list.stdout.close()

		reg = re.compile(r"^\s+(\d+)-")
		list_num = reg.match(grep.communicate()[0]).group(1)

		print("Installing \"Google Repository\"...")

		install = subprocess.check_output("echo y | android update sdk -u -a -t " + list_num, shell=True)
		print("Install completed.")

		return repo_path


# Unzip zip file
def unzip(source_filename, dest_dir):
	with zipfile.ZipFile(source_filename) as zf:
		for member in zf.infolist():
			zf.extract(member, dest_dir)


if __name__ == '__main__':
	main()
