#!/usr/bin/python
# Culled from https://gist.github.com/arubdesu/05b4172890450fa2d9e6
# Given a list of FW models and Thunderstrike patched FW versions,
# report on whether a machine has been patched.


import subprocess
import plistlib


__version__ = "1.0.0"
firmware_dict = {"MM51":"B12",
                 "MM61":"B08",
                 "MM71":"B03",
                 "MP61":"B15",
                 "MB81":"B06",
                 "IM121": "B21",
                 "IM131": "B08",
                 "IM141": "B11",
                 "IM142": "B11",
                 "IM143": "B11",
                 "IM144": "B10",
                 "IM151": "B03",
                 "MBP81": "B2A",
                 "MBP91": "B0B",
                 "MBA41": "B12",
                 "MBA51": "B03",
                 "MBA61": "B19",
                 "MBA71": "B06",
                 "MBP101": "B09",
                 "MBP102": "B08",
                 "MBP111": "B15",
                 "MBP112": "B15",
                 "MBP114": "B04",
                 "MBP121": "B07"}


cmd = ["/usr/sbin/system_profiler","SPHardwareDataType", "-xml"]
hdwe_stdout = subprocess.check_output(cmd)

output_plist = plistlib.readPlistFromString(hdwe_stdout)
full_rom = output_plist[0]["_items"][0]["boot_rom_version"]
(hdwe_code, _, current_fw_vers) = full_rom.split(".")

patched_vers = firmware_dict.get(hdwe_code)

if patched_vers:
    if current_fw_vers >= patched_vers:
        result = "Patched"
    else:
        result = ("Unpatched current version: %s required version: %s" %
                  (current_fw_vers, patched_vers))
else:
    result = "NotPatchable"

print "<result>%s</result>" % result