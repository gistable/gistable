import sys, os

package_dir = "packages"

sys.path.insert(0, package_dir)

for filename in os.listdir(package_dir):
    if filename.endswith((".zip", ".egg")):
        sys.path.insert(0, "%s/%s" % (package_dir, filename))