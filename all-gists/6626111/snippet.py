"""
1-script install xfce4 hotkeys for chromebook ubuntu

You might need to `killall xfconfd` or restart xfce for these to take effect.
"""

import os
import datetime

addage = [
    """      <property name="F9" type="string" value="volume down"/>\n""",
    """      <property name="F10" type="string" value="volume up"/>\n""",
    """      <property name="F6" type="string" value="brightness down"/>\n""",
    """      <property name="F7" type="string" value="brightness up"/>\n""",
    ]

where_to_add = """<property name="XF86WWW" type="string" value="exo-open --launch WebBrowser"/>"""

xml_fn = '~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml'
fn = os.path.expanduser(xml_fn)

text = open(fn).read()
if addage[0].strip() in text:
    print("Already added hotkeys, not modifying")
    exit()

bu_fn = fn + '.bu.' + datetime.datetime.now().isoformat()

with open(bu_fn, 'w') as fhand:
    fhand.write(text)

print('saved backup at %s' % bu_fn)

new_lines = []

for line in text.splitlines(True):
    new_lines.append(line)
    if where_to_add in line:
        new_lines += addage


new_text = ''.join(new_lines)

with open(fn, 'w') as fhand:
    fhand.write(new_text)

    
print('shortcut keys installed')