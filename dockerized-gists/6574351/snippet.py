'''
USAGE:

Let's say you have a "find_words_with_letter" function (not method) in a script called "script_name.py"...

    def find_words_with_letter(fileName, letter = "g"):
        #fxn code here

...you can then call the function in the script from  the command line - function name 1st argument, function args follow.

    python script_name.py find_words_with_letter FILENAME "B"


TIP:
- grep "def" script_name.py will give a quick list of functions for script and arguments
'''


if __name__ == "__main__":
    import sys
    assert sys.argv[1] in globals(), "Need name of fxn to run from command line!"
    fxnToRun = globals()[sys.argv[1]] 
    fxnToRun(*sys.argv[2:])
