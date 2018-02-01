import sublime
import sublime_plugin

'''
  __  __     __  __
 |  \/  |_ _|  \/  |
 | |\/| | '_| |\/| |_
 |_|  |_|_| |_|  |_(_)

Project: Examples of using custom dialog and messages in Sublime 2

Platform: tested only on a Mac

File Name: mrm_example_dialogs.py

Place file in your User folder

On Mac it is:
/Users/username/Library/Application Support/Sublime Text 2/Packages/User

On a Mac, this is hidden, find the folder by going to Finder and
Go | Go to Folder
~/Library/Application Support/Sublime Text 2
press ENTER


How to add a Command to the Command Palette  (Cmd-Shift-P) on Mac

1- Create a folder in
   Packages/Default/Default.sublime-commands
   There is same file in
   Packages/User/Default.sublime-commands
   don't modify files in Packages/Default, they will be overwritten when upgrading
   always use User folder for user specific settings

2- add this to file
[
    {
        "caption": "Run Example 1",
        "command": "example1"
    }
]


3- Then you can press Cmd-Shift_P, and type in: Ru
   and you will see this on list

Rev #1 - updated "print" to work with Python 3 and Python 2

'''

# ------------------------------------------------------------
# show_input_panel, status_message and message_dialog example
# to run this use:
# view.run_command("example1")
# at the command line in Sublime
# Note: Example1Command is expressed as example1 with the view.run_command("example1")

class Example1Command(sublime_plugin.TextCommand):
    def run(self, edit):
        # 'something' is the default message
        self.view.window().show_input_panel("Say something:", 'something', self.on_done, None, None)


    def on_done(self, user_input):
        # this is displayed in status bar at bottom
        sublime.status_message("User said: " + user_input)
        # this is a dialog box, with same message
        sublime.message_dialog("User said: " + user_input)


# ------------------------------------------------------------
# message_dialog example with cancel example
# to run this use:
# view.run_command("example2")
# at the command line in Sublime
# Note: Example2Command is expressed as example2 with the view.run_command("example2")



class Example2Command(sublime_plugin.TextCommand):
    def run(self, edit):



        # test of question box
        #  this no work, in 2 or version 3 beta sublime.question_box("thi sis a quetsion box")

        # this has OK button only
        sublime.message_dialog("Message goes here.")



        # this has two buttnos, Cancel and OKY
        sublime.ok_cancel_dialog("hello mrm", "OKY")
        #  no work sublime.errormessage_dialog("BIG ERROR")
        sublime.status_message("fred  ******************")  # this is at bottom

        # this has Cancel and OK button labeled OK Rob - and will respond depending on user action
        # Esc key will be taken as a Cancel

        if sublime.ok_cancel_dialog("OK ROB ?", "OK Rob"):
            # print will print to console
            print ("You Pressed OK")  # this will print to console if OK pressed.
        else:
            print ("You Pressed Cancel")


# ------------------------------------------------------------
# Dialog for error_message
# to run this use:
# view.run_command("example3")
# at the command line in Sublime
# Note: Example3Command is expressed as example3 with the view.run_command("example3")


class Example3Command(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.error_message("Must be and error!")
