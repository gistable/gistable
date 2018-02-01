import sublime, sublime_plugin
import os, commands
import json, re

import pprint

""" TODO:
	
	- have settings file with username/password/additional flags?
	- options menu, per file/folder commands 
        - ssh connection string 
        - last svn command?
	- svn status in the corner, on file save """

svnFlags = " --username=xxxxx --password=xxxx --non-interactive"

svnOptions = ['Subversion: Add',
			  'Subversion: Commit',
			  'Subversion: Delete',
			  'Subversion: Diff',
 			  'Subversion: Revert',
 			  'Subversion: Status',
			  'Subversion: Update']

""" Core Function Definitions for Plugin """
def doSystemCommand(commandText):
	return commands.getoutput(commandText)

""" Identical to doSystemCommand, but passes svnFlags to the
	command to give credentials and non-interactive flag. """
def doSvnCommand(svnCommand):
	svnCommandOutput = doSystemCommand(svnCommand + svnFlags)

	latestSvnCommand = svnCommand + svnFlags
	latestSvnOutput  = svnCommandOutput

	return svnCommandOutput


""" #################### SUBVERSION COMMAND ######################## """


""" The base class for the SVN plugin, sets up member variables,
	and modifies the status message in the case of the current directory
	not being a working copy. """
class SubversionCommand(sublime_plugin.TextCommand):
	def run(self, edit, svn_command, on_file):
		# Setup basic member variables
		SubversionCommand.edit   = edit
		SubversionCommand.view   = self.view
		SubversionCommand.window = sublime.active_window()
		SubversionCommand.current_filename = SubversionCommand.view.file_name()

		svnFile 	= open("/home/dan/.config/sublime-text-2/Packages/SVN/settings.json")
		svnSettings = json.load(svnFile)
		
		# pprint.pprint(svnSettings)


		# Bail early if the current directory isn't a working copy
		if (SubversionCommand.isWorkingCopy(self) == False):
			sublime.status_message("Subversion Plugin can not run because this is not a working copy of SVN.")
			return False

		if (svn_command == "opt"):
			pprint.pprint(on_file)
			return

		# Switch based on the svn_command
		if (svn_command == "add"):
			SubversionCommand.add(self)
		elif (svn_command == "commit"):
			SubversionCommand.commit(self)
		elif (svn_command == "delete"):
			SubversionCommand.delete(self)
		elif (svn_command == "diff"):
			SubversionCommand.diff(self)
		elif (svn_command == "revert"):
			SubversionCommand.revert(self)
		elif (svn_command == "status"):
			SubversionCommand.status(self)
		elif (svn_command == "update"):
			SubversionCommand.update(self)

	def isWorkingCopy(self):
		svnStatus = doSvnCommand("svn status " + self.current_filename)

		if ("not a working copy" in svnStatus):
			return False
		else:
			return True

	def add(self):
		svnAdd = doSvnCommand("svn add " + self.current_filename)

		# State whether or not it's been added, or already under version control
		if ("already under version control" in svnAdd):
			sublime.status_message("SVN: File already under version control.")
		elif (re.match("^A", svnAdd)):
			sublime.status_message("SVN: File added.")

	def commit(self):
		self.window.show_input_panel(
								"Commit Message: ",
								"Changes to " + self.current_filename,
								self.commitOnDone,
								None,
								self.commitOnCancel)
	
	def commitOnDone(self, commitMessage):
		commitCommand = 'svn commit -m "' + commitMessage  + '" ' + self.current_filename
		svnCommit  	  = doSvnCommand(commitCommand)

		commitStatus = re.search("Committed revision \d+\.", svnCommit)

		if (commitStatus):
			statusMessage = "SVN: " + commitStatus.group(0)
		else:
			statusMessage = svnCommit

		sublime.status_message(statusMessage)

	def commitOnCancel(self):
		sublime.status_message("SVN: Commit aborted.")

	def delete(self):
		self.window.show_input_panel(
								"Confirm Delete ",
								"Enter to Confirm, Escape to Abort.",
								self.deleteOnDone,
								None,
								self.deleteOnCancel)

	def deleteOnDone(self, inputMessage):
		svnDelete = doSvnCommand("svn delete --force " + self.current_filename)

		# @todo Needs to close the current view

		sublime.status_message(svnDelete)

	def deleteOnCancel(self):
		sublime.status_message("SVN: Delete aborted.")
		return

	def diff(self):
		svnDiff = doSvnCommand("svn diff " + self.current_filename)

		# @todo - Doesn't work! :P
		if (svnDiff == ""):
			sublime.status_message("SVN: Diff showed no modifications.")
			return

		# Create new view for the diff
		svnDiffView = sublime.Window.new_file(self.view.window())

		# Insert diff content
		svnDiffView.insert(self.edit, 0, svnDiff)

		# Set to be a scratch/readonly buffer
		svnDiffView.set_scratch(True)
		svnDiffView.set_read_only(True)
		svnDiffView.set_name("svn diff")

	def revert(self):
		# Require view isn't in the middle of loading
		if (self.view.is_loading() == False):
			svnRevert = doSvnCommand("svn revert " + self.current_filename)

			if (svnRevert == ""):
				svnRevert = "SVN: No changes to revert."

			sublime.status_message(svnRevert)
			
			sublime.active_window().focus_view(sublime.active_window().active_view())
			# @todo Needs to close current view

		
	def status(self, filename=False):
		if (filename == False):
			filename = self.current_filename

		svnStatus = doSvnCommand("svn status " + filename)

		if (re.search("\n", svnStatus)):
			# Create new view for status if it's multi-line
			svnStatusView = sublime.Window.new_file(self.view.window())

			# Insert status content
			svnStatusView.insert(self.edit, 0, svnStatus)

			# Set to be a scratch/readonly buffer
			svnStatusView.set_scratch(True)
			svnStatusView.set_read_only(True)
			svnStatusView.set_name("svn status")
		elif (svnStatus == ""):
			svnStatus = "SVN: File unchanged."
		
		sublime.status_message(svnStatus)

	def update(self, detailsInScratch=False):
		svnUpdate = doSvnCommand("svn update " + self.current_filename)

		# Get information about the update
		updateData = SubversionCommand.getUpdateData(self, svnUpdate)

		# If there are conflicts, automatically open in new buffer
		# for analysis.
		if (updateData['has_conflicts']):
			detailsInScratch = True
 
 		# Couldn't find an "At revision..." line?
		if (detailsInScratch or updateData['updated_line'] == False):
			svnStatusView = sublime.Window.new_file(view.window())
			svnStatusView.insert(self.edit, 0, svnUpdate)

			svnStatusView.set_scratch(True)
			svnStatusView.set_read_only(True)
			svnStatusView.set_name("svn update")		
		else:
			sublime.status_message("SVN: " + updateData['updated_line'])



	def getUpdateData(self, svnUpdate):
		conflictPattern = "^C"
		updatedPattern  = "^At revision"

		hasConflicts = False
		updatedLine  = False

		svnUpdate = svnUpdate.split("\n")

		# Find if any conflicts occurred, and get final "At revision" line
		for svnLine in svnUpdate:
			if (re.match(conflictPattern, svnLine)):
				hasConflicts = True
				continue;
			elif (re.match(updatedPattern, svnLine)):
				updatedLine = svnLine

		updateData = { 	"has_conflicts": hasConflicts,
					    "updated_line":  updatedLine }

		return updateData