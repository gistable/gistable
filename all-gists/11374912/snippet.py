"""
===============
pep8_tonizer.py
===============
    This script can be used to make python code, that is being edited on Notepad++, \
         to comply with infamous PEP8 coding style [http://bit.ly/pep8]
    By default, autopep8 only makes whitespace changes. So does this script.
    
    However, this script depends on following:
    
        *  Python Script for Notepad++ [http://npppythonscript.sourceforge.net]
           ---------------------------------------------------------------------
           This create the runtime environment for executing python scripts on Notepad++ objects.
           Install by downloading via:
               . http://npppythonscript.sourceforge.net/download.shtml
                 (better choose the *.msi option)
        
        *  autopep8  [http://pypi.python.org/pypi/autopep8]
           ------------------------------------------------
           This is the main library module for checking & converting to PEP8-complying code.
               It, in turn, depends on pep8 package. [https://github.com/jcrocholl/pep8]
               Installing steps via pip:

                   1.  pip install --upgrade pep8
                   2.  pip install --upgrade autopep8
                   
    
    __project__ = "pep8_tonizer : PEP8-fixer plugin for Notepad++"
    __author__  = "Khaled Monsoor <k@kmonsoor.com>"
    __license__ = "MIT"
    __version__ = "0.4.0"
    
    
    Installation:
    -------------
        1. Install pep8
        2. Install autopep8
        3. install Python Script for Notepad++
        4. download "pep8_tonizer.py" to a convenient location
        5. find & copy pep8.py & autopep8.py to <Notepad++ install dir>\\plugins\PythonScript\lib
        6. start notepad++
        6. Go to Menu >> Plugins >> Python Script
        7. click "New script"
        8. find & select "pep8_tonizer.py"
        9. Good job, all set.
        
    Usage:
    ------
        After opening / creating any python source file,
            1. Go to Menu >> Plugins >> Python Script >> Scripts
            2. Click "pep8_tonizer.py"
            3. Whoa !
            
    TODO list:
    ----------
        1. adding options for autopep8 style configurations, currently it works as default
        2. automate the setup processes(dependency check as well) as much as possible
        3. integrate the whole process into just 1 or 2 steps

"""

import autopep8 as p8

current_text_on_editor = editor.getText()
pep8_complying_code = p8.fix_code(current_text_on_editor)
editor.clearAll()
editor.insertText(0, pep8_complying_code)

# Inform the user that we've done it
notepad.messageBox(
    "pep8-toization completed with default autopep8 options", "pep8_tonizer", 0)
