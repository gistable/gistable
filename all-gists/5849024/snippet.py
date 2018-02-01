import re, fileinput
import pyPEG
from pyPEG import parse, parseLine
from pyPEG import keyword, _and, _not, ignore
import datetime

## Taken from https://gist.github.com/bertspaan/3059017 and translated to English. It is Working well BUT if you find any errors, please comment!

numbers = [
"zero",
"one",
"two",
"three",
"four",
"five",
"six",
"seven",
"eight",
"nine",
"ten",
"eleven",
"twelve",
"thirteen",
"fourteen",
"fifteen",
"sixteen",
"seventeen",
"eighteen",
"nineteen"
"twenty",
"twenty one",
"twenty two",
"twenty three",
"twenty four",
"twenty five",
"twenty six",
"twenty seven",
"twenty eight",
"twenty nine",
"thirty",
"thirty one",
"thirty two",
"thirty three",
"four thirty",
"thirty five",
"thirty six",
"thirty seven",
"thirty eight",
"thirty nine",
"forty",
"forty one",
"forty two",
"forty three",
"forty four",
"forty five",
"forty six",
"forty seven",
"forty eight",
"forty nine",
"fifty",
"fifty one",
"fifty two",
"three fifty",
"four fifty",
"fifty five",
"fifty six",
"fifty seven",
"fifty eight",
"fifty nine",
"sixty"
]

times = [
	"thirteen past 5",
	"12 56",
	"12:56",
	"twelve thirty",
	"nine fifteen",
	"quarter to two",
	"ten to two",
	"three to half ten",
	"13 hour 52",
	"three thirty",
	"seven thirty",
	"eighteen fifteen",
	"seven",
	"nine",
	"8 hour",
	"eighteen fifteen",
]

def number():	return re.compile(r"\w+")
def half():		return re.compile(r"half")
def hours():	return -1, half, number, -1, keyword("hours")
def sign():		return [re.compile(r"to"), re.compile(r"past")]
def minutes():	return number
def time():		return [		
					(minutes, sign, hours),
					(minutes, sign, hours),
					(hours, -1, ":", minutes),
					hours
				]

def string_to_int(str):
	if str == "quarter":
		return 15		
	for i in range(0, 60):
		if str == numbers[i]:
			return i
		
	return int(str)

def to_time(ast):
	minutes_str = ""
	hours_str = ""
	half = False
	sign = 1
	
	# ast is tuple (ast, ''). skip weird '' part:
	ast = ast[0]

	for symbol in ast:
		name = symbol[0]
		value = symbol[1]
		if name == "hours":
			if len(value) == 2:
				# Has 'half'
				half = True
				hours_str = value[1][1]
			else:
				hours_str = value[0][1]
		elif name == "minutes":
			minutes_str = value[0][1]
		elif name == "sign":
			if value[0] == "voor":
				sign = -1

	minutes = 0

	if len(hours_str) > 0:
		minutes = string_to_int(hours_str) * 60

	if half:
		minutes -= 30
		
	if len(minutes_str) > 0:
		minutes += sign * string_to_int(minutes_str)

	hours = minutes // 60
	minutes = minutes - (60 * hours)
	
	today = datetime.date.today() + datetime.timedelta(days=1)
	return datetime.datetime.combine(today, datetime.time(hours, minutes))

for time_str in times:	
	ast = parseLine(textline=time_str, pattern=time(), resultSoFar=[])	
	print time_str, " => ", to_time(ast)

