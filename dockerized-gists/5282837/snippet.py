import re
import os.path
import datetime
import os
import time


# Path to the minecraft statistics file
mine_path = "FULL_PATH_TO_/stats_user_unsent.dat"

# Path to the own log
log_path = "/Users/mutsuda/Code/log_stats.html"

# One Minecraft tick is equivalent to 0.052 seconds
eq = 0.052

# The regular expression that will match the gameplay Ticks
ticks_regex = re.compile('{"1100":.*}');

# Return the current number of ticks in a Minecraf stats file
def get_ticks(f):
	for line in f:
		time = ticks_regex.findall(line)
		if time:
			return time[0].split(':')[1].replace("}","")

# Gets the latest data from the log file
def get_latest_ticks(f):
	last = os.popen("tail -n 1 %s" % log_path).read()
	return last.split('|')[1]

# Operates the current ticks with the old ones
def get_result(aT,lT):
	delta_ticks = int(aT) - int(lT)
	delta_time = datetime.timedelta(seconds=delta_ticks*eq)
	return ("[" + str(datetime.datetime.now())+ "]" +  
		"|" + str(aT)+ "|" + str(delta_time))

# Writes the resulting line back to the log file
def write_result(f,result):
	f.write(result+"\n")

def main():
	latest_ticks = 0

	# Read latest ticks
	if os.path.exists(log_path):

		# If the file already exists, we obtain the latest ticks
		latest_ticks = get_latest_ticks(open(log_path,'r'))
	
	# We get the ticks we have now in the minecraft stats file
	actual_ticks = get_ticks(open(mine_path, 'r'))

	# We obtain the line we the delta in ticks and time
	result = get_result(actual_ticks,latest_ticks);

	# We now write the result into our statistics file
	write_result(open(log_path,"a"),result)


if __name__ == "__main__":
    main()