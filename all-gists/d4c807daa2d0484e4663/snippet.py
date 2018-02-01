from cmd import Cmd

class testCmd(Cmd):
	prompt = "hoge) "
    def __init__(self):
        Cmd.__init__(self)

	def do_exe(self, arg):
		print "do anything"

	def help_exe(self):
		print "help : exe"

if __name__ == '__main__':
	testCmd().cmdloop()