import sublime, sublime_plugin
import sys,os,re
#script should go in Pacakges/FSharpAutocomplete/FSharpAutocomplete.py
#pexpect should go in Packages/FSharpAutocomplete/lib
#to make it load 'everything' from the lib folder.
def installpath(path):
	if path not in sys.path:
		sys.path.insert(0, path)

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)
lib_path = os.path.join(__path__, 'lib')

installpath(lib_path)
#Now do the import
import pexpect #3.0b1 for Python>3.2 from https://github.com/pexpect/pexpect/releases/tag/3.0b1
#An object wrapping the pexepct calls to 'mono fsautocomplete.exe'
class AutocompleteService():
  #from https://github.com/fsharp/fsharpbinding
  #I am not sure where this should 'go' maybe in the lib folder as above?
	prog = "<WHERE YOU PUT IT>/fsharp-lib/fsharpbinding-master/FSharp.AutoComplete/bin/Debug/fsautocomplete.exe"
	service = pexpect.spawn("mono " + prog)#create the process when you create the object
	service.setecho(False)#so what we send is not printed

	def read_from_service(self):
		response = self.service.expect(['<<EOF>>'])
		return self.service.before.strip().decode("UTF-8")
	
	def get_service_data(self):
		data = self.read_from_service()
		match = re.match(".+?([A-Z]+:.+)",data,re.DOTALL)
		if match: 
			return match.group(1)
		return data

	def sendrequest(self,request):
		self.service.sendline(request)
		return self.get_service_data()

	def sendrequest_dontwait(self,request):
		self.service.sendline(request)

	def sendfile(self,path):
		#using strip because of trailing lines
		for line in open(path,'r'): self.service.sendline(line.strip('\n'))
		self.service.sendline('<<EOF>>')                         
		return self.get_service_data()

	def terminate(self):
		self.service.terminate(force=True)

acs = AutocompleteService()#create the object

#---------------------------------------------

def isFsharp(filename):#simple check could be a lot smarter I imagine
	if filename:
		return '.fs' in filename or '.fsx' in filename
	return False

#send the file for parsing, don't wait for it to complete.
def parsefile(filename):
	acs.sendrequest_dontwait('parse "'+filename+'"')
	result = acs.sendfile(filename)

def prepcomp(item):
	return (item+"\tFSharp Autocomplete",item)

#when the file is parsed, this can be called to get the completions list
def getcompletions(filename,rowcol):
	result = acs.sendrequest('completion "'+filename+'" '+str(rowcol[0])+' '+str(rowcol[1]))
	if 'INFO:' not in result and 'ERROR:' not in result:
		lines = result.split('\r\n')
		comps = list(list(map(prepcomp,lines))[1:])
		return comps
	else: print(result)
	return 0
	
#Listen for the actual events
class FSharpAutocomplete(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		if isFsharp(view.file_name()): 
			return getcompletions(view.file_name(),view.rowcol(locations[0]))
		else: return 0#do nothing
	def on_load(self,view):
		if isFsharp(view.file_name()): parsefile(view.file_name())
	def on_post_save(self,view):
		if isFsharp(view.file_name()): parsefile(view.file_name())
