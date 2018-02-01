from datetime import datetime, time

def dateDiffInSeconds(date1, date2):
  timedelta = date2 - date1
  return timedelta.days * 24 * 3600 + timedelta.seconds

def daysHoursMinutesSecondsFromSeconds(seconds):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	return (days, hours, minutes, seconds)

leaving_date = datetime.strptime('2012-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
now = datetime.now()

print "%d days, %d hours, %d minutes, %d seconds" % daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date))