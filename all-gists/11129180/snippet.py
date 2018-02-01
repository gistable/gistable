# Requires pdfminer, icalendar
# both are easy_install'able

import itertools, re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from datetime import date, time, datetime, timedelta
from icalendar import Calendar, Event

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

def gen_ical_from_file(filename, output_filename="invite.ical"):
    result = convert_pdf_to_txt(filename).split("\n")

	dates = list(filter(lambda x : x.startswith("Data: "), result))
	dates = list(date(*(int(i) for i in d.replace("Data: ","").split("-"))) for d in dates)

	times_and_notes = list(itertools.dropwhile(lambda x: not x.startswith("Volta:"), 
		itertools.takewhile(lambda x: "Bilhete de Identidade" not in x, result)))[2:-3]

	times_and_notes = times_and_notes[:3], times_and_notes[-3:]
	times = list(list(re.findall("\d\d:\d\d", t ) 
			for t in filter(lambda x: x.startswith("Partida:"), leg))[0][0] 
		for leg in times_and_notes)
	times = list(time(*(int(i,10) for i in t.split(":"))) for t in times)


	cal = Calendar()
	for trip_date,trip_time,notes in zip(dates, times, times_and_notes):
		dt = datetime.combine(trip_date, trip_time)
		evt = Event()
		evt.add("summary", notes[0])
		evt.add("dtstart", dt)
		evt.add("dtend", dt+timedelta(hours=3))
		evt.add("description", "\n".join(notes))
		cal.add_component(evt)

	with file(output_filename,"wb") as output:
		output.write(cal.to_ical())
	print("Wrote ical to "+output_filename)

if __name__=="__main__":
	import sys, os.path
	output_filename = "invite.ical"
	if(len(sys.argv) == 1): raise Exception("Must be called with pdf filepath")
	if(len(sys.argv) == 3): output_filename = sys.argv[2]
	if(not os.path.exists(sys.argv[1])): raise Exception("File "+sys.argv[1]+" does not exist")
	gen_ical_from_file(sys.argv[1], output_filename)