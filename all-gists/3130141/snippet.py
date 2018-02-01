import sublime
import sublime_plugin
import subprocess
import struct
import tempfile
import threading
import time
import traceback
import os
import re
import Queue

cdb_shutting_down = False
cdb_process = None

# This queue contains command we wish to send to CDB.
cdb_pend = Queue.Queue()
cdb_commands = []
cdb_prompt = re.compile(r"([0-9]+):([0-9]+)>$", re.M)
cdb_command = re.compile(r"^([0-9]+):([0-9]+)>", re.M)

def cdbworker():
	global cdb_process
	global cdb_pend
	cdb_current = None
	current_output = ""
	abort = False

	while True:
		try:
			if cdb_process == None or cdb_process.poll() != None:
				break

			# Try and wait for a command.
			if cdb_current == None:
				try:
					cdb_current = cdb_pend.get(True, 1)
					if cdb_current.get_text().strip() != "":
						cdb_process.stdin.write(cdb_current.get_text() + "\r\n")
						cdb_current.insert_text("\n")
				except:
					cdb_current = None

			if cdb_current != None:
				if not cdb_prompt.search(current_output):
					current_output = current_output + cdb_process.stdout.read(1)
				elif cdb_current != None: # tell the command that it has completed
					cdb_current.insert_text(current_output.strip())
					cdb_current.commit()
					current_output = ""
					cdb_current = None

			if current_output.endswith("\n"):
				cdb_current.insert_text(current_output.strip() + "\n")
				current_output = ""

			# TODO: Deal with interactive debugging - the debugger could
			# do something without us requesting it

		except:
			traceback.print_exc()
			abort = True

	if cdb_process != None and (not abort) and cdb_current != None:
		text = cdb_process.stdout.read()
		cdb_current.insert_text(text)

	print("CDB has closed")

# We use this to tell the backend thread what to do
class CdbCommand:
	def __init__(self, view, edit, region, text):
		self.view = view
		self.text = text
		self.region = region
		self.edit = edit

	def insert_text(self, insert):
		sublime.set_timeout(lambda: self.insert_text_impl(insert), 100)

	def commit(self):
		sublime.set_timeout(lambda: self.commit_impl(), 100)

	def insert_text_impl(self, insert):
		end = self.region.end()
		length = self.view.insert(self.edit, end, insert)
		self.view.show(end + length)
		self.update_regions(length)

	def commit_impl(self):
		cdb_commands.remove(self)
		self.update_status()

	def get_text(self):
		return self.text

	def update_regions(self, length):
		region = self.region
		end = self.region.end()
		for command in cdb_commands:
			if command.region.begin() >= end or command.region.intersects(region):
				command.region = sublime.Region(command.region.a + length, command.region.b + length)
		self.update_status()

	def update_status(self):
		if len(cdb_commands) > 0:
			self.view.set_status('cdb', "SublimeCDB is waiting %i commands to complete" % len(cdb_commands))
		else:
			self.view.erase_status('cdb')


# This command launches CDB
class CdbExecute(sublime_plugin.TextCommand):
	def run(self, edit):
		global cdb_process
		global cdb_shutting_down

		if cdb_process == None or cdb_process.poll() != None:
			self.launchcdb(edit)
		else:
			self.sendtocdb(edit)

	def launchcdb(self, edit):
		global cdb_process
		global cdb_shutting_down

		# Get the starting command
		sel = self.view.sel()[0]
		line_region = self.view.full_line(sel)
		command = self.view.substr(line_region)

		commandline = ""
		workdir = ""
		
		# Determine the architecture
		if command.startswith("x64 ") or command.startswith("x86 "):
			workdir = "C:\\windbg\\" + command[0:3]
			commandline = workdir + "\\cdb.exe "
			command = command[4:]
		else:
			self.view.replace(edit, line_region, "x86 dump C:\\foo.dmp")
			return

		# Determine the command
		if command.startswith("dump "):
			commandline = commandline + "-z \"" + command[5:] + "\""
		else:
			self.view.replace(edit, line_region, "x86 dump C:\\foo.dmp")
			return

		print "Running: %s" % commandline
		print "In directory: %s" % workdir

		cdb_process = subprocess.Popen(commandline, shell=True, cwd=workdir,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

		# Queue the first command to get the initial output from CDB.
		self.pend(edit, line_region, "")

		t = threading.Thread(target=cdbworker)
		t.start()
		
	def sendtocdb(self, edit):
		global cdb_process
		global cdb_shutting_down

		sels = self.view.sel()
		end_sel = 0
		# Support multiple selections
		for sel in sels:
			# Get all the lines in the selection
			lines = self.view.lines(sel)

			end = sel.end()
			if end_sel < end:
				end_sel = end

			# Check each line
			for line in lines:
				line_content = self.view.substr(line)

				if line_content.startswith(">"):
					line_content = line_content[1:]
				elif cdb_command.search(line_content):
					pos = line_content.index(">") + 1
					line_content = line_content[pos:]
				else:
					line_content = ""

				if line_content != "":
					self.pend(edit, line, line_content)
		sels.clear()
		sels.add(sublime.Region(end_sel, end_sel))

	def pend(self, edit, sel, content):
		command_push = CdbCommand(self.view, edit, sel, content)
		cdb_commands.append(command_push)
		cdb_pend.put(command_push)
		command_push.update_status()
