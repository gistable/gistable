
# python3 amifucked.py
# Public Domain

import platform, subprocess

# Feel free to poke me in the comments if I missed something here
TELEMETRY_MAYBE = {
  "KB2952664": "Compatibility update for upgrading Windows 7",
  "KB2976978": "Performs and collect compatibility appraiser logs in order to ease the upgrade experience to Windows 10",
  "KB2990214": "Update that enables you to upgrade from Windows 7 to a later version of Windows",
  "KB3044374": "Update that enables you to upgrade from Windows 8.1 to Windows 10",
  "KB3021917": "Update to Windows 7 SP1 for performance improvements",
  "KB3050265": "Updates Windows Update Client for Windows 7 (changes system files to support upgrade)",
  "KB3050267": "Updates Windows Update Client for Windows 8.1 (changes system files to support upgrade)",
  "KB3065987": "Updates Windows Update Client for Windows 7 and Windows Server 2008 R2 (changes system files to support upgrade)",
  "KB3075851": "Updates Windows Update Client for Windows 7 and Windows Server 2008 R2 (changes system files to support upgrade)"
}
TELEMETRY = {
  "KB3022345": "Update for customer experience and diagnostic telemetry",
  "KB3035583": "Installs the 'Get Windows 10' app in Windows 8.1 and Windows 7 SP1",
  "KB3072318": "Update for Windows 8.1 OOBE to upgrade to Windows 10",
  "KB3068708": "(replaces KB3022345) Update for customer experience and diagnostic telemetry",
  "KB3075249": "Update that adds telemetry points to consent.exe in Windows 8.1 and Windows 7",
  "KB3015249": "Update that adds telemetry points to consent.exe in Windows 8.1 and Windows 7",
  "KB3080149": "Update for customer experience and diagnostic telemetry",
  "KB2977759": "Compatibility update for Windows 7 RTM (for Windows Customer Experience Improvement Program)",
}

YES = 1
NO = 0
MAYBE = -1

def isfucked():
  system = platform.system()

  if system != "Windows":
    return NO, "You're on {}!".format(system)

  release, version, csd, ptype = platform.win32_ver()
  if release == "10":
    return YES, "You've already downgraded to Windows 10!"

  proc = subprocess.Popen("wmic /output:stdout qfe get hotfixid",
    shell=True, stdout=subprocess.PIPE)
  hotfixes = proc.stdout.read().splitlines()
  hotfixes = [i.strip().decode("utf-8") for i in filter(bool, hotfixes)]

  kblist = []
  fucked = NO
  for kb in hotfixes:
    if kb in TELEMETRY_MAYBE:
      if fucked == NO: fucked = MAYBE
      kblist.append("? {}: {}".format(kb, TELEMETRY_MAYBE[kb]))
    elif kb in TELEMETRY:
      fucked = YES
      kblist.append("! {}: {}".format(kb, TELEMETRY[kb]))

  kblist.sort(key=lambda x: x[0])
  return fucked, "Installed telemetry updates:\n" + "\n".join(kblist)

if __name__ == "__main__":
  print("Checking Windows updates...")

  fucked, output = isfucked()
  if fucked == YES:
    print("You are FUCKED.")
  elif fucked == MAYBE:
    print("You MIGHT be fucked.")
  else:
    print("You are not fucked (yet).")

  print(output)
