import datetime

dias = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']
meses = ['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

startdate = datetime.date(2012,1,1)
while(startdate.year == 2012):
	if startdate.weekday() in [5,6]:
		print "%s %d %s" % (meses[startdate.month],startdate.day,dias[startdate.weekday()])
	startdate += datetime.timedelta(1)