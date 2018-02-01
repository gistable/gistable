#! /usr/bin/env python
import sys, subprocess, os, pytz
from datetime import datetime, timedelta
from optparse import OptionParser
from dateutil.parser import parse as dateparse

def get_dates_and_shas(branch, start, end, interval):
  """Gets the relevant shas given the start date, end date and interval on 
	the given branch.

	Args:
		branch (str): name of the branch to perform the analysis on.
		start (datetime): the start date. Defaults to the start of the project.
		end (datetime): the end date. Defaults to now.
		interval (int): the interval in days between the diffs.
	Returns:
		list of (date, sha) tuples
	"""
	shas = []
	dates = []
	if interval == 0:
		# If interval is 0, simply get all the non-merge commits and find 
		# their dates
		revlist = subprocess.Popen(['git', 'rev-list', '--since', str(start), 
					'--before', str(end), '--no-merges', branch], 
					stdout=subprocess.PIPE)
		# Read the SHAs to get the exact date they were committed onto the 
		# master branch
		for sha in revlist.stdout.readlines():
			shas.append(sha[:-1])
			dates.append(dateparse(subprocess.Popen(['git', 'show', 
								'--format=format:%ci', 
								'--shortstat', sha[:-1]], 
								stdout=subprocess.PIPE)
								.stdout.readline()))
	else:
		# If interval is not 0, we want to record the 'state' of the branch at 
		# a given time, which is the first sha on the branch before the given date.
		current = end
		while current >= (start + timedelta(days=interval)):
			shas.append(subprocess.Popen(['git', 'rev-list', '-n1', 
						'--first-parent', '--before', str(current), 
						branch], stdout=subprocess.PIPE)
						.stdout.readline()[:-1])
			dates.append(current)
			current = current - timedelta(days=interval)
		# Add the start date so it doesn't matter whether interval precisely matches
		# the amount of days in between start and end.
		shas.append(subprocess.Popen(['git', 'rev-list', '-n1', '--first-parent', 
						'--before', str(start), branch], 
						stdout=subprocess.PIPE)
						.stdout.readline()[:-1])
		dates.append(start)
	return zip(dates, shas)



def get_churn_with_interval(dateshas, excludestr):
	"""Calculates the total churn of commits described in dateshas after 
	filtering out the excluded paths.

	Args:
		dateshas (datetime, str): A tuple of datetimes and commit shas.
		excludestr: A grep-friendly regular expression.
	Returns:
		int: The cumulative amount of churned lines.
	Outputs:
		On stdout: a CSV of the form sha;date;churn.
	"""
	print "sha1;date1;sha2;date2;churn" # CSV header line
	total = 0
	date, sha = dateshas[0]
	for prevdate, prevsha in dateshas[1:]:
		diff = None
		if excludestr:
			# See function get_churn_per_commit for an explanation per 
			# process call
			files = subprocess.Popen(['git', 'diff', '-w', '-C', 
						 '--name-status', '--format=format:', 
						prevsha, sha], stdout=subprocess.PIPE)
			cut = subprocess.Popen(['cut', '-f2,3'], stdin=files.stdout, 
						stdout=subprocess.PIPE)
			grep = subprocess.Popen(['grep', '-v', excludestr], 
						stdin=cut.stdout, stdout=subprocess.PIPE)
			xargs = subprocess.Popen(['xargs', '-L', '500', 'git', 'diff', 
						'-w', '-C', '--shortstat', 
						'--format=format:', prevsha, sha, '--', 
						'dummy'], stdin=grep.stdout, 
						stdout=subprocess.PIPE)
			diff = xargs.stdout.readlines()
		else:
			files = subprocess.Popen(['git', 'diff', '-w', '-C', 
						'--shortstat', '--format=format:', 
						prevsha, sha], stdout=subprocess.PIPE)
			diff = files.stdout.readlines()

		# Remove leading/trailing newlines
		diff = [x[:-1] for x in diff if x != '\n']

		# Because of the xargs approach, there might be multiple result 
		# lines. Iterate over all of them and sum the churn. That is, if 
		# there are actually results left after directory filtering
		churn = 0
		for line in diff:
			if len(line) > 0:
				added = int(line.split()[3])
			churn += added
		total += churn
		print "%s;%s;%s;%s;%d" % (prevsha[:8], str(prevdate), sha[:8], str(date), churn)
		date, sha = prevdate, prevsha

	return total


def get_churn_per_commit(dateshas, excludestr):
	"""Calculates the total churn of commits described in dateshas after 
	filtering out the excluded paths.

	Args:
		dateshas (datetime, str): A tuple of datetimes and commit shas.
		excludestr: A grep-friendly regular expression.
	Returns:
		int: The cumulative amount of churned lines.
	Outputs:
		On stdout: a CSV of the form sha;date;churn.
	"""
	print "sha;date;churn" # CSV header line
	total = 0
	for date, sha in dateshas:
		commit = None
		if excludestr:
			# Example command with filtering:
			# git show abcde -w -C --name-status --format=format: 
			#		Outputs all the changed files with just their filenames, 
			#		as paths from the repository root. -w flag ignores 
			#		whitespace differences, -C flag detects move moves and 
			#		renames and ignores those.
			# cut -f2,3:
			#		Cuts out the filename (column 2) and the rename 
			#		destination (column 3, if exists). This is done to not 
			#		have the M/A/D/R modification indicator from the 
			#		--name-status output.
			# grep -v '^Documentation/':
			#		Filters out all the files which are in the specified 
			#		folders.
			# xargs -L 500 git show abcde -w -C --shortstat -- dummy
			#		xargs carries all the files that grep outputs over to git 
			#		show, which formats the	result into a line of the form 
			#		'X files changed, Y insertions(+), Z deletions(-)'.
			#		Using xargs because OS X has a wonky and unpredictable 
			#		argument list length limit,	so this should makes the 
			#		script more portable. 'dummy' is specified to ensure an 
			#		empty set from grep does not lead to 'git show' showing 
			#		everything.
			show = subprocess.Popen(['git', 'show', sha, '-w', '-C', 
						'--name-status', '--format=format:'], 
						stdout=subprocess.PIPE)
			cut = subprocess.Popen(['cut', '-f2,3'], stdin=show.stdout, 
						stdout=subprocess.PIPE)
			grep = subprocess.Popen(['grep', '-v', excludestr], 
						stdin=cut.stdout, stdout=subprocess.PIPE)
			xargs = subprocess.Popen(['xargs', '-L', '500', 'git', 'show', 
						sha, '-w', '-C', '--shortstat', 
						'--format=format:', '--', 'dummy'], 
						stdin=grep.stdout, stdout=subprocess.PIPE)
			commit = xargs.stdout.readlines()
		else:
			# If there is no excludestr, we can simply ask for the shortstat 
			# information.
			show = subprocess.Popen(['git', 'show', sha, '-w', '-C', 
						'--shortstat', '--format=format:'], 
						stdout=subprocess.PIPE)
			commit = show.stdout.readlines()

		# Remove leading/trailing newlines
		commit = [x[:-1] for x in commit if x != '\n']

		# Because of the xargs approach, there might be multiple result 
		# lines. Iterate over all of them and sum the churn. That is, if there 
		# are actually results left after directory filtering
		churn = 0
		for line in commit:
			if len(line) > 0:
				try:
					added = int(line.split()[3])
				except:
					added = 0
			churn += added
		if churn > 0:
			total += churn
			print "%s;%s;%d" % (sha[:8],str(date), churn)

	return total

def vararg_callback(option, opt_str, value, parser):
	"""Function vararg_callback
	
	An extention on OptParser to parse a varying amount of argument, in this 
	case used for the -x flag.
	"""
	assert value is None
	value = []

	def floatable(str):
		try:
			float(str)
			return True
		except ValueError:
			return False

	for arg in parser.rargs:
		# Stop on options like --foo 
		if arg[:2] == "--" and len(arg) > 2:
			break
		# Stop on -a, but not on negative numbers
		if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
			break
		value.append(arg)

	del parser.rargs[:len(value)]
	setattr(parser.values, option.dest, value)

if __name__ == '__main__':
	parser = OptionParser("Usage: %prog [options] <path> <branch>")
	parser.add_option("-s", "--start", dest="start", help="Start date to check from, format DD-MM-YYYY")
	parser.add_option("-e", "--end", dest="end", help="End date to stop check at, format DD-MM-YYYY")
	parser.add_option("-i", "--interval", dest="interval", help="Number of days in between considered commits")
	parser.add_option("-x", "--exclude", dest="exclude", action="callback", callback=vararg_callback, help="Folders to be excluded")
	(options, args) = parser.parse_args()
	if len(args) < 2:
		print "Usage: %s [options] <path> <branch>" % sys.argv[0]
		sys.exit(-1)
	start, end, interval, exclude_dirs = None, None, 0, []
	if options.start:
		start = datetime.strptime(options.start, "%d-%m-%Y")
		start = pytz.UTC.localize(start)
	if options.end:
		end = datetime.strptime(options.end, "%d-%m-%Y")
		end = pytz.UTC.localize(end)
	if options.interval:
		interval = int(options.interval)
		if interval < 0:
			print "Sorry, interval can only be 0 or larger"
			sys.exit(1)
	if options.exclude:
		exclude_dirs = options.exclude

	# Create the exclude regular expression
	excludestr = ("^{}\|"*len(exclude_dirs))[:-2].format(*exclude_dirs)
	# Change the cwd so all commands are run in the correct folder
	os.chdir(args[0])
	dateshas = get_dates_and_shas(args[1], start, end, interval)
	if interval == 0:
		total = get_churn_per_commit(dateshas, excludestr if exclude_dirs else "")
		print "Total churn between %s and %s, based on individual commits: %d" % (str(start), str(end), total)
	else:
		total = get_churn_with_interval(dateshas, excludestr if exclude_dirs else "")
		print "Total churn between %s and %s, with intervals of %d days: %d" % (str(start), str(end), interval, total)
