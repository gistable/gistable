#!/usr/bin/python
"""
Collect Info

To be used in a Jamf Pro workflow to prompt a user/tech for info

Heavily cribbed from Jamf's iPhone ordering script:
https://github.com/jamfit/iPhone-Ordering
"""

import AppKit
import sys
import os
import Tkinter
import tkFont
import tkMessageBox
import subprocess
import plistlib

# Path to Jamf binary
JAMF = "/usr/local/bin/jamf"

# base64-encoded GIF for "icon" at the top of the GUI
# MUST BE A GIF!
mbp_icon = '''
R0lGODdh+gCWAMQAAAAAAElJSVJSUlxcXGFhYW5ubnNzc3x8fIWFhY+Pj6WlpampqbKysry8vMbGxsjI
yNTU1Nzc3OHh4enp6fLy8v///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAkKABYALAAA
AAD6AJYAAAX/oCWOZGmeaKqubOu+cCzPdG3feK7vfO//wKBwSCwaj8ikcslsOp/QqHRKrVqv2Kx2y+16
v+CweEwum8/otHrNbrvf8Lh8Tq/b7/i8fs/PGQ6AgYKDhIWGh4iJiouMjY6GBn0pCAwRE5eYmZqbnJ2e
n6ChoqOkpZ0RDAiSJQkSFa+wsbKztLW2t7i5uru8vbkTCasiBxO+xsfHEg/IzM25EgerBAzO1davEAsU
19zNDASSBRHd5OXm568RBZLE6O7v8LsT0X3tsBIQ+fr7/P3+/wADChxIsKDBg/1cwZrHrhisCA4iSpxI
saLFixgzatzIsaPHjxXHLaTHx94rCQ4e/6hcybKly5cwY8qcSbOmzZs4WToQ+YphPYcnU+YcSrSo0aNH
d8byWRJoBZRIo0qdSvWm0pENY0GtyrWrV6NXe5LcY/Kp0K9o06rVybMCU7JOt66dS5dqWLdj9ZSVW7ev
35x33+qNe/av4cMwA+fNs7cw4seIFWe95xiy5b6Sf2qtfLmz2sxNN3sePRc0XNGkU381PRi16td22wpm
TBi2bamsabu+zXtobjyNewsHLHsx8NrDk9P8fSe48ueJi08OCr16S+Z2nFu3jr2O9u3Qu9P5Dl65+Dnk
yw8/Lye9+t7s47h/fzs+nPn0Ydt/gz+/6v1u9OcfaQC2IeCAnhXIxv+BCF6m4BoMNgjZg2pEKGFk0mlG
2YW2UZiGhRz+5SEaIIaIWYahbWhiaiOeUeKKpaF4moowJihjazTW6OCNuuWo44Q8Hrfbj4+1aMaLRHpl
ZBlIJsnVkmQ06WRsSxnXHHJTHgblGFJmGdWWYnTpZVJBXjnkmHSBGYaYaBKlJhhstklcldOZJeeJdGpI
3Z1plpkdlnx+5qd3gAaK1ptfxGnoTIh6oeiiMTXaxaOQviQpF5RWet2g4xWqKZVY6Wnnp11dukWmpD5g
qhaokrpqFq1++ioWsWo66xW1VnqrFblCumsVvS76KxXBGjrsFMUGeqwUyfK5bBTN3vksFNHKOe3/E9W2
ea0T2aK5bRPdjvktE+F6Oe4S5WZ5rhLpTrluEu06+S4S8SY57xH1EnmvEfn+uG8R/er4LxEB1zjwEAXD
eLAQZUEE0sMQRyzxxBQvHERZE0ig8cYcd+zxxyCHLPLIJJds8skoe+zUbELG4/LL8bBsJsw019yNzH/a
rPPOyOBMKM9AB42Lz50KbfTRYoXTAEJMN/1PBFBHLfXUVFft9NVXN7AOlw5gnc9wChRgwNhkl2322WYX
oMBwXkPggJUMO4W0OeqgbffdY4sztztE/1DW3uU0gMDghBdu+OGGNwA4On378Pfi3VAg+eSUV2555ZCf
03gPCMid+eegNzOBoCrwKrDA6ainrvrqrLfu+uuwxy777LTXbvvtuM+uANxCiF222L7jLfzwxBdv/PHI
J6/88swDnza2B/wRCPPUV2/99dhnn7wg0gP7x9iAaC/++OSXP3743/M+BdnRm+/++/DH334kwtRv//34
56///vz37///AAygAAdIwAIa8IAITKACF8jABjrwgRCMoAQnSMEKWvCCGMygBjfIwQ56MAQAOw==
'''

class App:
    def __init__(self, main):
        """Main GUI window"""
        self.main = main
        self.main.resizable(False, False)
        self.main.title("Assign User Information")

        self.main.protocol("WM_DELETE_WINDOW", self.cancel)
        self.main.call('wm', 'attributes', '.', '-topmost', True)
        x = (self.main.winfo_screenwidth() - self.main.winfo_reqwidth()) / 2
        y = (self.main.winfo_screenheight() - self.main.winfo_reqheight()) / 3
        self.main.geometry("+{0}+{1}".format(x, y))
        # w, h = self.main.winfo_screenwidth(), self.main.winfo_screenheight()
        # self.main.overrideredirect(1)
        # self.main.geometry("%dx%d+0+0" % (w, h))

        bgcolor = '#F0F0F0'
        self.main.tk_setPalette(background=bgcolor,
                                  highlightbackground=bgcolor)

        font = tkFont.nametofont('TkDefaultFont')
        font.config(family='system',
                    size=14)
        self.main.option_add("*Font", font)

        menu_bar = Tkinter.Menu(self.main)
        self.main.config(menu=menu_bar)

        print('Starting app')

        # Input variables
        self.input_assigned_user = Tkinter.StringVar()
        self.input_assigned_dept = Tkinter.StringVar()
        self.input_asset_tag = Tkinter.StringVar()

        # Get icon
        self.icon_data = Tkinter.PhotoImage(data=mbp_icon)

        # Icon Frame
        self.frame1 = Tkinter.Frame(self.main)
        self.photo_canvas = Tkinter.Canvas(self.frame1, width=250, height=150)
        self.photo_canvas.pack()
        self.icon = self.photo_canvas.create_image(0, 0, anchor="nw", image=self.icon_data)
        self.frame1.pack(padx=40, pady=(30, 5))

        # Title Frame
        self.frame2 = Tkinter.Frame(self.main)
        title_label = Tkinter.Label(self.frame2, text="Assign Device")
        title_label.grid(row=0, column=0)
        self.frame2.pack(padx=40, pady=(10,5))

        # Inputs frame
        self.frame3 = Tkinter.Frame(self.main)

        user_label = Tkinter.Label(self.frame3, text="Assigned User:")
        user_label.pack()
        self.entry_assigned_user = Tkinter.Entry(self.frame3,
                                                 background='white',
                                                 textvariable=self.input_assigned_user,
                                                 width=30)
        self.entry_assigned_user.pack(pady=(0, 20))

        dept_label = Tkinter.Label(self.frame3, text="Department Code:")
        dept_label.pack()
        self.entry_assigned_dept = Tkinter.Entry(self.frame3,
                                                background='white',
                                                textvariable=self.input_assigned_dept,
                                                width=30)
        self.entry_assigned_dept.pack(pady=(0, 20))

        asset_label = Tkinter.Label(self.frame3, text="Asset Tag:")
        asset_label.pack()
        self.entry_asset_tag = Tkinter.Entry(self.frame3,
                                                background='white',
                                                textvariable=self.input_asset_tag,
                                                width=30)
        self.entry_asset_tag.pack(pady=(0, 20))

        self.frame3.pack(padx=40, pady=5)

        # Buttons
        self.frame5 = Tkinter.Frame(self.main)
        submit = Tkinter.Button(self.frame5, text='Assign', height=1, width=8, command=self.submit)
        submit.pack(side='right')
        cancel = Tkinter.Button(self.frame5, text='Cancel', height=1, width=8, command=self.cancel)
        cancel.pack(side='right')
        self.frame5.pack(padx=40, pady=(5, 30))

        # Add GUI padding

    def cancel(self):
        """Exit the GUI"""
        print('User has closed the app')
        self.main.destroy()

    def submit(self):
        """
        Do something with the data submitted

        You can do...well, anything you want here. 

        I use the gathered data to set the computer's name to conform with
        our naming convention and submit the asset tag and end user's username
        to the JSS.
        """
        print('User has submitted')

        # Our naming convention is:
        # [department code]-[M for Mac][L for latop or D for desktop][asset tag]
        # i.e. IT-ML00000
        #
        # Fun Fact! Our asset tags are prepended with the year the device was
        # purchased, so a quick glance at a hostname tells us where it goes,
        # the platform and form factor, and an approximate age. We order them
        # from myassettag.com each year this way.

        # Clean up the submitted end username and make it lowercase
        # Splitting each character of the input with split(), then re-joining
        # with ''.join() strips all whitespace as opposed to strip() which
        # just cleans the head and tail
        i_user = ''.join(self.input_assigned_user.get().lower().split())
        # Clean up the department code and make it uppercase
        i_dept = ''.join(self.input_assigned_dept.get().upper().split())
        # Just strip whitespace from the asset tag
        i_atag = ''.join(self.input_asset_tag.get().split())

        # Determine model for assigning name
        # https://github.com/gregneagle/psumac2014_python/blob/master/4_3_0_machine_info.py
        cmd = ['/usr/sbin/system_profiler', 'SPHardwareDataType', '-xml']
        output = subprocess.check_output(cmd)
        info = plistlib.readPlistFromString(output)
        hardware_info = info[0]['_items'][0]
        if "Book" in hardware_info['machine_model']:
            model_id = "L"
        else:
            model_id = "D"

        # Assemble hostname
        hostname = "{}-M{}{}".format(i_dept, model_id, i_atag)

        print "Hostname: {}".format(hostname)

        # Rename the computer
        cmd = [JAMF, 'setComputerName', '-name', hostname]
        rename = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        (out, err) = rename.communicate()
        if rename.returncode == 0:
            print "Set computer name to {}".format(hostname)
        else:
            print "Rename failed!"
            sys.exit(1)

        # Submit new inventory
        cmd = [JAMF, 'recon', '-endUsername', i_user, '-assetTag', i_atag]
        inventory = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        (out, err) = inventory.communicate()
        if inventory.returncode == 0:
            print "Submitted inventory to JSS"
        else:
            print "Inventory update failed!"
            sys.exit(1)

        self.main.destroy()


def main():
    # Prevent the Python app icon from appearing in the Dock
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info['CFBundleIconFile'] = u'PythonApplet.icns'
    info['LSUIElement'] = True

    root = Tkinter.Tk()
    app = App(root)
    # Have the GUI appear on top of all other windows
    AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
    rdata = app.main.mainloop()

    sys.exit(0)

if __name__ == '__main__':
    main()
