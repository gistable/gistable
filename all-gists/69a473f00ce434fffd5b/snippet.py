#!/usr/bin/python
"""Identify or remove files known to be involved in Adware/Malware
infection.

Most of the code applies to building a list of malware files. Thus,
both extension attribute and removal handling are included.

Cleans files as a Casper script policy; thus, it expects four total
arguments, the first three of which it doesn't use, followed by
--remove

"""

import glob
import os
import re
import shutil
import sys
import syslog


# https://support.apple.com/en-us/ht203987
known_malware = {
    '/System/Library/Frameworks/v.framework',
    '/System/Library/Frameworks/VSearch.framework',
    '/Library/PrivilegedHelperTools/Jack',
    '/Library/InputManagers/CTLoader/',
    '/Library/Application Support/Conduit/',
    '/Applications/SearchProtect.app',
    '/private/etc/launchd.conf',
    '/Applications/Genieo',
    '/Applications/InstallMac',
    '/Applications/Uninstall Genieo',
    '/Applications/Uninstall IM Completer.app',
    '/usr/lib/libgenkit.dylib',
    '/usr/lib/libgenkitsa.dylib',
    '/usr/lib/libimckit.dylib',
    '/usr/lib/libimckitsa.dylib',
    '/Library/PrivilegedHelperTools/com.genieoinnovation.macextension.client',
    '/Library/Frameworks/GenieoExtra.framework',
    '/Library/LaunchAgents/com.genieo.completer.update.plist',
    '/Library/LaunchAgents/com.genieo.engine.plist',
    '/Library/LaunchAgents/com.genieoinnovation.macextension.client.plist',
    '/Library/LaunchAgents/com.genieoinnovation.macextension.plist',
    '/Library/LaunchDaemons/com.genieoinnovation.macextension.client.plist',
    '/Library/LaunchDaemons/Jack.plist'
    '/Users/*/Library/Internet Plug-Ins/ConduitNPAPIPlugin.plugin',
    '/Users/*/Library/Internet Plug-Ins/TroviNPAPIPlugin.plugin',
    '/Users/*/Library/Application Support/Genieo/',
    '/Users/*/Library/Application Support/com.genieoinnovation.Installer/',
    '/Users/*/Conduit/',
    '/Users/*/Trovi/',
    '/Users/*/Library/Caches/com.Conduit.takeOverSearchAssetsMac',
    '/Users/*/Library/Caches/com.VSearch.bulk.installer',
    '/Users/*/Library/Caches/com.VSearch.VSinstaller',
    '/Users/*/Library/LaunchAgents/com.genieo.completer.download.plist',
    '/Users/*/Library/LaunchAgents/com.genieo.completer.ltvbit.plist',
    '/Users/*/Library/LaunchAgents/com.genieo.completer.update.plist',
    '/Users/*/Library/Preferences/com.genieo.global.settings.plist.lockfile',
    '/Users/*/Library/Preferences/com.geneio.settings.plist.lockfile',
    '/Users/*/Library/Preferences/com.geneio.global.settings.plist',
    '/Users/*/Library/Saved Application State/com.genieo.RemoveGenieoMac.savedState',
    '/Users/*/Library/Saved Application State/com.VSearch.bulk.installer.savedstate',
    '/Users/*/Library/LaunchAgents/com.jdibackup.ZipCloud.autostart.plist'}

found_malware = {match for filename in known_malware for match in
                 glob.glob(filename)}

# Look for "ProjectX" variants.
# This adware seems to have a different name each time it pops up.
# Apple's solution is too broad. We look at the files Apple suggests,
# but then also search within to see if they are calling a known
# binary file, "agent.app/Contents/MacOS/agent".
projectx_files = {
    '/Library/LaunchAgents/com.*.agent.plist',
    '/Library/LaunchDaemons/com.*.helper.plist',
    '/Library/LaunchDaemons/com.*.daemon.plist',
}

projectx_candidates = {match for filename in projectx_files for match in
                 glob.glob(filename)}

agent_regex = re.compile('.*/Library/Application Support/(.*)/Agent/agent.app/Contents/MacOS/agent')
for candidate in projectx_candidates:
    with open(candidate, 'r') as candidate_file:
        launchd_job = candidate_file.read()

    if re.search(agent_regex, launchd_job):
        found_malware.add(candidate)
        # If we find a Launch[Agent|Daemon] that has ProgramArguments
        # which runs "agent", find the unique name for this instance.
        # We can then use it to find the Application Support folder.
        obfuscated_name = re.search(agent_regex, launchd_job).group(1)
        found_malware.add('/Library/Application Support/%s' % obfuscated_name)

# Is this an EA or a script execution (Casper scripts always have 3
# args, so we can't just use the first argument.
if len(sys.argv) == 1:
    # Extension attribute (First arg is always script name).
    result = '<result>'
    if found_malware:
        result += 'True\n'
        for item in enumerate(found_malware):
            result += "%d: %s\n" % item
    else:
        result += 'False'

    print('%s</result>' % result)

elif "--remove" in sys.argv:
    # Removal script.
    syslog.syslog(syslog.LOG_ALERT, "Looking for malware")
    for item in found_malware:
        try:
            if os.path.isdir(item):
                shutil.rmtree(item)
            elif os.path.isfile(item):
                os.remove(item)
            syslog.syslog(syslog.LOG_ALERT, "Removed malware file:  %s" % item)
        except OSError as e:
            syslog.syslog(syslog.LOG_ALERT,
                          "Failed to remove malware file:  %s, %s" % (item, e))
