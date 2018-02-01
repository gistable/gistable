"""
CTTCX 1.1
Convert CardioTrainer CSV file to TCX file.
Copyright (c) 2012  Dragan Bosnjak <draganHR@gmail.com>
https://twitter.com/dragan
"""
from optparse import OptionParser
from xml.dom.minidom import Document
import os
import csv
import re
import datetime

usage = "usage: %prog [options] input output"
parser = OptionParser(usage=usage)
parser.add_option("-p", "--pretty", action="store_true", dest="pretty", default=False, help="Pretty XML output")
parser.add_option("-s", "--split", type="int", dest="split", default=None, help="Number of workouts in each output file, don't split if not specified")

(options, args) = parser.parse_args()

if len(args) < 1:
    parser.error("Wrong number of arguments")
    
if options.split is not None and options.split < 1:
    parser.error("Invalid split value")
    
filename = args[0]
    
try:
    csvfile = open(filename, "rb")
    csvsample = csvfile.read(1024)
    csvfile.seek(0)
    dialect = csv.Sniffer().sniff(csvsample)
    has_header = csv.Sniffer().has_header(csvsample)
    reader = csv.reader(csvfile, dialect)
except Exception, e:
    parser.error(e)
    
if not has_header:
    parser.error("Invalid CSV format: header not found!")

csvheader = reader.next()
if len(csvheader)!=11:
    parser.error("Invalid CSV format: wrong number of columns!")

print "Parsing %s..." % filename

counter = 0
i = 0
k = 1
row = True
while row and (options.split is None or options.split>counter):
    
    if counter==0:
        doc = Document()
        tcd = doc.createElement("TrainingCenterDatabase")
        tcd.setAttribute("xmlns", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
        tcd.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        tcd.setAttribute("xsi:schemaLocation", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")
        
        doc.appendChild(tcd)
        Activities = doc.createElement("Activities")
        tcd.appendChild(Activities)

    try:
        row = reader.next()

        row = {csvheader[i]: row[i] for i in range(len(row))}
        
        row['DistanceMeters'] = str(1000*float(row['Distance']))
        
        DurationParts = re.search(r"(\d+):(\d+):(\d+)$", "0:0:0:%s" % row['Duration'])
        row['Duration'] = 3600 * int(DurationParts.group(1)) + 60 * int(DurationParts.group(2)) + int(DurationParts.group(3))
        
        row['DateTime'] = datetime.datetime.strptime("%s %s" % (row['Date'], row['Time']), "%A %b.%d %Y %I:%M %p")
        
        row['Climb'] = float(row['Climb'])
        
        row['Notes'] = []
        if row['Name']:
            row['Notes'].append(row['Name'])
        if row['Climb']:
            row['Notes'].append("Elevation: %s" % row['Climb'])
        
        # Activity
        Activity = doc.createElement("Activity")
        Activity.setAttribute('Sport', row['Type'])
        Activities.appendChild(Activity)
    
        # Id
        Id = doc.createElement("Id")
        Id.appendChild(doc.createTextNode("%s" % row['DateTime']))
        Activity.appendChild(Id)
        
        # Lap
        Lap = doc.createElement("Lap")
        Lap.setAttribute('StartTime', datetime.datetime.strftime(row['DateTime'], "%Y-%m-%dT%H:%M:%S%Z"))
        Activity.appendChild(Lap)
        
        TotalTimeSeconds = doc.createElement("TotalTimeSeconds")
        TotalTimeSeconds.appendChild(doc.createTextNode(str(row['Duration'])))
        Lap.appendChild(TotalTimeSeconds)
        
        DistanceMeters = doc.createElement("DistanceMeters")
        DistanceMeters.appendChild(doc.createTextNode(row['DistanceMeters']))
        Lap.appendChild(DistanceMeters)
        
        Calories = doc.createElement("Calories")
        Calories.appendChild(doc.createTextNode(row['Calories']))
        Lap.appendChild(Calories)
        
        Intensity = doc.createElement("Intensity")
        Intensity.appendChild(doc.createTextNode("Active"))
        Lap.appendChild(Intensity)
        
        TriggerMethod = doc.createElement("TriggerMethod")
        TriggerMethod.appendChild(doc.createTextNode("Manual"))
        Lap.appendChild(TriggerMethod)
        
        Track = doc.createElement("Track")
        Lap.appendChild(Track)
        
        # Notes
        if row['Notes']:
            Notes = doc.createElement("Notes")
            Notes.appendChild(doc.createTextNode("\n".join(row['Notes'])))
            Activity.appendChild(Notes)
            
        i+=1
        counter+=1
        
    except StopIteration:
        # End of file
        row = None
        
    if row is None or options.split==counter:
        counter = 0
        
        # Write XML to file
        if len(args)>1: filename = args[1]
        else: filename = "export-%s.tcx" % (datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        if options.split is not None: filename = "%s.%04d.tcx" % (os.path.splitext(filename)[0], k)
        print "Exporting to %s..." % filename
        
        try:
            f=open(filename, "wb")
            f.write(doc.toprettyxml() if options.pretty else doc.toxml())
            f.close()
        except Exception, e:
            parser.error(e)
        k += 1
    
print "Done!"
