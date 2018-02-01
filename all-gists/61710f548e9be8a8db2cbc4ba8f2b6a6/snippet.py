#!/usr/bin/python

# Completely uninstall Office 2016, as per:
# https://support.office.com/en-us/article/Uninstall-Office-2016-for-Mac-eefa1199-5b58-43af-8a3d-b73dc1a8cae3
# and
# https://support.office.com/en-us/article/Troubleshoot-Office-2016-for-Mac-issues-by-completely-uninstalling-before-you-reinstall-ec3aa66e-6a76-451f-9d35-cba2e14e94c0?ui=en-US&rs=en-US&ad=US


import glob
import os
import shutil
import subprocess


def main():
    apps = ("Microsoft Excel", "Microsoft OneNote",
            "Microsoft Outlook", "Microsoft PowerPoint",
            "Microsoft Word")

    # Step 1: Remove Office 2016 for Mac applications.
    for app in apps:
        shutil.rmtree(os.path.join("/Applications", app + ".app"),
                      ignore_errors=True)

    # Step 2: Remove Supporting Files.
    # rm Licensing, stop jobs.
    job = ("/Library/LaunchDaemons/"
           "com.microsoft.office.licensingV2.helper.plist")
    subprocess.call(["launchctl", "unload", job])

    license_files = (
        job,
        "/Library/PrivilegedHelperTools/com.microsoft.office.licensingV2.helper",
        "/Library/Preferences/com.microsoft.office.licensingV2.plist")
    for license_file in license_files:
        try:
            os.remove(license_file)
        except OSError:
            print "File '{}' has already been removed.".format(license_file)

    # rm Containers
    container_names = ("errorreporting", "Excel", "netlib.shipassertprocess",
                       "Office365ServiceV2", "Outlook", "Powerpoint",
                       "RMS-XPCService", "Word", "onenote.mac")
    containers = ("com.microsoft.{}".format(name) for name in container_names)

    for container in containers:
        present_containers = glob.glob(
            os.path.join("/Users/*/Library/Containers/", container))
        for present_container in present_containers:
            shutil.rmtree(present_container)

    # rm Group Containers
    # Please note: This is where local-only data lives, so back it up
    # if you care about it!
    group_containers = ("UBF8T346G9.ms", "UBF8T346G9.Office",
                        "UBF8T346G9.OfficeOsfWebHost")

    for container in group_containers:
        present_containers = glob.glob(
            os.path.join("/Users/*/Library/Group Containers/", container))
        for present_container in present_containers:
            shutil.rmtree(present_container)

    # Step 3: Remove keychain entries.
    # During testing, I had three seemingly identical items with "value"/"gena"
    # string "MSOpenTech.ADAL.1". Deleting only affects one at a time, so
    # iterate.
    exit_code = 0
    while exit_code == 0:
        exit_code = subprocess.call(
            ["security", "delete-generic-password", "-G", "MSOpenTech.ADAL.1"])

    subprocess.call(
        ["security", "delete-generic-password", "-l",
         "Microsoft Office Identities Cache 2"])
    subprocess.call(
        ["security", "delete-generic-password", "-l",
         "Microsoft Office Identities Settings 2"])

    # Step 4: Remove Office 2016 for Mac icons from the dock.
    dockutil_available = False
    try:
        subprocess.call(["dockutil", "--version"])
        dockutil_available = True
    except OSError:
        pass

    if dockutil_available:
        for app in apps:
            subprocess.call(["dockutil", "--remove", app, "--allhomes"])
    else:
        print "dockutil not present: skipping dock item removal."

    # Step 5: Restart.
    # No thanks.

    # Help Munki by removing receipts.
    receipts = (
        "com.microsoft.package.Microsoft_Word.app",
        "com.microsoft.package.Microsoft_Excel.app",
        "com.microsoft.package.Microsoft_PowerPoint.app",
        "com.microsoft.package.Microsoft_OneNote.app",
        "com.microsoft.package.Microsoft_Outlook.app",
        "com.microsoft.package.component",
        "com.microsoft.pkg.licensing",
        "com.microsoft.package.Fonts",
        "com.microsoft.package.Frameworks",
        "com.microsoft.package.Proofing_Tools")
    for receipt in receipts:
        subprocess.call(["pkgutil", "--forget", receipt])


if __name__ == "__main__":
    main()
