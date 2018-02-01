import os
class Session(object):
    def __init__(self):
        self.version = '0.2.2'
        print('PyCMD {}\nInteract with the cmd simulator to run python files. Type \'help\' for assistance.'.format(self.version))
        try:
            self.h = open('history.pycmd', 'r+')
        except:
            print('Found no history file, creating new...')
            self.h = open('history.pycmd', 'w+')
        self.history = self.h.read()
        self.running = True
        self.HELPMSG = """
            PyCMD Version {} Help:

            Commands:
            help    Display this message
            exec    Execute a python source file
            quit    Exit PyCMD

            Instructions:
            Enter a command (no arguments).
            The command will give instructions and ask for any inputs required.
        """.format(self.version)
    def displayHelp(self):
        print(self.HELPMSG)
    def runFile(self):
        filename = input('Enter file name to open and run: ')
        contents = ''
        if filename == '!!':
            if self.history == '':
                print('History is blank- filenames will be added once a program is executed.')
            else:
                print('Opening ' + self.history + '...')
                try:
                    f = open(self.history, 'r')
                    contents = f.read()
                    contents = compile(contents, '', 'exec')
                except FileNotFoundError:
                    print('Could not open {}: file does not exist.'.format(self.history))
        else:
            try:
                f = open(filename, 'r')
                contents = f.read()

                self.history = filename
                #print('wrote ' + filename + ' to history')
                contents = compile(contents, '', 'exec')
            except FileNotFoundError:
                print('Could not open file: file does not exist.')
        try:
            if not contents == '':
                print('\nProgram Output:\n\n=================\n')
                exec(contents)
                print('\n=================\n\nProgram Complete.\n')
                f.close()
        except BaseException as e:
            print('Program exited with errors: {}'.format(e))
    def main(self):
        while self.running:
            command = input('> ').split(' ')
            command.append('')
            cmd = command[0]
            if cmd == 'exec':
                self.runFile()
            elif cmd == 'help':
                self.displayHelp()
            elif cmd == 'quit':
                print('Exiting PyCMD...')
                self.running = False
            else:
                print('Command not found.')
        print('Overwriting history...')
        self.h.seek(0)
        self.h.truncate()
        self.h.write(self.history)
        print('Closing setup files...')
        self.h.close()
session = Session()
session.main()
print('PyCMD- operation completed without errors.')
