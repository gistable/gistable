#!/usr/bin/env python3

import cfscrape # install with `pip install cfscrape`
import re
import os
import json
from packaging.version import Version

def build_multimc_patch_json(mc_version, optifine_version):
	patch = {
		"name": "OptiFine",
		"order": 200,
		"mainClass": "net.minecraft.launchwrapper.Launch",
		"fileId": "optifine.OptiFine",
		"version": mc_version + "_" + optifine_version,
		"mcVersion": mc_version,
		"+tweakers": [],
		"+libraries": [
			{ "name": "net.minecraft:launchwrapper:1.12" },
			{
				"name": "optifine:OptiFine:" + mc_version + "_" + optifine_version,
				"MMC-hint": "local"
			}
		]
	}

	if Version(mc_version) >= Version("1.10.2"):
		patch["+tweakers"].append("optifine.OptiFineTweaker")
	else:
		patch["+tweakers"].append("org.multimc.hacks.OptiFineHackTweaker")
		patch["+libraries"].append({
			"name": "org.multimc.hacks:OptiFineHack:1",
			"MMC-absoluteUrl": "http://files.multimc.org/downloads/OptiFineHack-1.jar"
		})

	return json.dumps(patch)

optifine_downloadx_re = re.compile(b"<a href=\"(downloadx\\?f=.+?)\">Download OptiFine_.+?\\.jar<\\/a>")

multimc_optifine_lib_path_template = "libraries/optifine/OptiFine/{version}/OptiFine-{version}.jar"
multimc_instance_path_template = "instances/{instance}"

def download_optifine_jarfile(url):
	scraper = cfscrape.create_scraper()

	page = scraper.get(url).content

	url2 = optifine_downloadx_re.search(page).group(1)

	dl_url = "http://optifine.net/" + url2.decode("utf-8")

	jarfile = scraper.get(dl_url).content

	if jarfile == b"File not found.\n": # I wish it 404'd
		return None

	return jarfile

def write_optifine_jarfile(version, content):
	filename = multimc_optifine_lib_path_template.format(version=version)

	os.makedirs(os.path.dirname(filename), exist_ok=True)

	with open(filename, "wb") as f:
		f.write(content)

def write_patch_json(instance_name, content):
	filename = multimc_instance_path_template.format(instance=instance_name) + "/patches/optifine.json"

	if not os.path.isdir(os.path.dirname(filename)):
		os.mkdir(os.path.dirname(filename))

	with open(filename, "w") as f:
		f.write(content)

def check_instance_exists(instance):
	return os.path.isdir(multimc_instance_path_template.format(instance=instance))

def check_optifine_exists(version):
	return os.path.exists(multimc_optifine_lib_path_template.format(version=version))

def get_instance_mc_version(instance):
	filename = multimc_instance_path_template.format(instance=instance) + "/instance.cfg"

	with open(filename, "r") as f:
		for line in f:
			if line[:15] == "IntendedVersion":
				return line[16:-1]

# todo: generate this table
latest_optifine_versions = {
	Version("1.12.1"): "HD_U_C5",
	Version("1.12.0"): "HD_U_C5",
	Version("1.11.2"): "HD_U_C3",
	Version("1.11.0"): "HD_U_C3",
	Version("1.10.2"): "HD_U_E3",
	Version("1.10.0"): "HD_U_E3",
	Version("1.9.4"): "HD_U_E3",
	Version("1.9.2"): "HD_U_E3",
	Version("1.9.0"): "HD_U_E3",
	Version("1.8.9"): "HD_U_H8",
	Version("1.8.8"): "HD_U_H8",
	Version("1.8.0"): "HD_U_H8",
	Version("1.7.10"): "HD_U_D8",
	Version("1.7.2"): "HD_U_E8"
}

def main():
	instance = input("Enter Instance name: ")

	if not check_instance_exists(instance):
		print("Instance '{}' does not exist.".format(instance))
		exit(1)

	mc_version = get_instance_mc_version(instance)

	if not mc_version:
		print("Instance '{}' has an invalid cfg file format.".format(instance))
		exit(1)

	if Version(mc_version) in latest_optifine_versions:
		print("Suggested OptiFine version: " + latest_optifine_versions[Version(mc_version)])

	# todo: display all possible optifine versions?
	# perhaps automatically use the suggested one if available

	optifine_version = input("Enter OptiFine version: ")

	if not check_optifine_exists(mc_version + "_" + optifine_version):
		url = "http://optifine.net/adloadx?f=OptiFine_" + mc_version + "_" + optifine_version + ".jar"

		jarfile = download_optifine_jarfile(url)

		if jarfile is None:
			print("Invalid OptiFine version.")
			exit(1)

		write_optifine_jarfile(mc_version + "_" + optifine_version, jarfile)

	write_patch_json(instance, build_multimc_patch_json(mc_version, optifine_version))

if __name__ == "__main__":
	main()
