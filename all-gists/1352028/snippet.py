import sublime, sublime_plugin, os

class TailCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		from datetime import datetime

		filtertext = "FLO"

		# open sublime console
		self.view.window().run_command("show_panel", { "panel": "console", "toggle": "true" })

		# show log as output
		folder = self.view.window().folders()[0]
		print 
		print datetime.now()
		print ">> open " + folder + "/log/development.log:"
		log = os.popen("tail " + folder + "/log/development.log -n 200 | grep " + filtertext).readlines()
		if len(log) == 0:
			print ">> no matches for FLO"
		else:
			for line in log:
				print ">> " + line