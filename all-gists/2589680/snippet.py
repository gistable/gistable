#
# Given a useragent string, return these results:
# Android version, device model name, type (tablet/phone)
#

import re
def android_details (useragent):
    result = {}
    result["aVersion"] = "Other"
    result["amake"] = "Other"
    result["aType"] = "Other"
    if ("Silk-Accelerated" in useragent) or ("Kindle Fire" in useragent):
      result["aVersion"] = "2.3.4"
      result["amake"] = "Kindle Fire"
      result["aType"] = "Tablet"
      return result
    if ("Android" in useragent):
      if "Mobile" in useragent:
        result["aType"] = "Phone"
      else:
        result["aType"] = "Tablet"
      # Match Opera browser's useragent
      if "Opera" in useragent:
        regex = "Opera/[^\s]* \(Android ([^;]*); [^;]*; Opera [^/]*/[^;]*; .*"
        match = re.match(regex, useragent, re.M|re.I)
        result["aVersion"] = match.group(1)
        if "Tablet" in useragent:
          result["aType"] = "Tablet"
        else:
          result["aType"] = "Phone"
        return result
      # Most common useragent
      regex = ".*Android (.*); [^;]*; (.*) Build/[^\)]*\) .*"
      match = re.match(regex, useragent, re.M|re.I)
      if not match:
        # Some useragents don't have the "Build/" keyword
        regex = ".*Android ([^;]*); [^;]*; ([^/]*)/[^\)]*\) .*"
        match = re.match(regex, useragent, re.M|re.I)
      if not match:
        # Some leave out the language name (particularly the Galaxy Nexus models)
        regex = ".*Android (.*); (.*) Build/[^\)]*\) .*"
        match = re.match(regex, useragent, re.M|re.I)
      # Nothing matched, just return the "Other" result
      if not match:
        return result
      result["aVersion"] = match.group(1)
      result["amake"] = match.group(2)
      result["amake"] = aModelHumanName(result["amake"])
      return result

#
# Return human-readable name of model
#
def aModelHumanName (model):
    lookup = {
        "GT P7510": "Samsung Galaxy Tab 10.1 (WiFi)",
        "Transformer TF101": "Asus Transforrmer TF101",
        "A500": "Acer Iconia Tab A500",
        "Xoom": "Motorola Xoom",
        "AT100": "Toshiba AT100",
        "BNTV250": "Nook Tablet (16gb)",
        "GT P7500": "Samsung Galaxy Tab 10.1 (WiFi+3G)",
        "Transformer Prime TF201": "Asus Transformer Prime TF201",
        "MZ604": "Motorola Xoom (32gb, WiFi)",
        "A100": "Acer Iconia Tab A100",
        "MZ601": "Motorola Xoom (3G)",
        "GT P7310": "Samsung Galaxy Tab 8.9 (WiFi)",
        "A501": "Acer Iconia Tab A501",
        "K1": "Lenovo IdeaPad K1",
        "LG V909": "LG Optimus Pad 8.9",
        "LIFETAB_P9514": "Medion LifeTab",
        "GT P6210": "Samsung Galaxy Tab 7 (16gb, WiFi)"
    }
    if model in lookup:
        return lookup[model]
    else:
        return model

# 
# Code to test this
# 
def test():
    print "Device 1: ",
    print android_details("Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; DROIDX Build/4.5.1_57_DX8-51) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")
    result = android_details("Opera/9.80 (Android 2.2; Linux; Opera Tablet/ADR-1203051631; U; ja) Presto/2.10.254 Version/12.00")
    print "Device 2 type: " + result["aType"]

# 
# Running this should output:
# Device 1:  {'aType': 'Phone', 'amake': 'DROIDX', 'aVersion': '2.3.4'}
# Device 2 type: Tablet
# 
test()