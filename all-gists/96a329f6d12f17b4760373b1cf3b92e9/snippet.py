#!/bin/env python3


from bs4 import BeautifulSoup
import urllib.request
import subprocess
import re
import sys
import random

try:
	file = str(sys.argv[1])
except IndexError:
	print("Please provide a file as an argument")
	exit(-1);


atis_website="https://atis.informatik.kit.edu/1194.php"

site_info = urllib.request.urlopen(atis_website).read()

soup = BeautifulSoup(site_info, 'html.parser')



#Getting only black and white printers
printer_full = subprocess.run(['lpstat', '-p', '-d'], stdout=subprocess.PIPE).stdout.decode('utf-8')
printer_full = subprocess.run(['lpstat', '-p', '-d'], stdout=subprocess.PIPE).stdout.decode('utf-8')


printers = []
table=soup.find_all('td')
for line in printer_full.split("\n"):
	

	try:
	         name = line.split(" ")[1]        
	except IndexError:
		break
	   
	
	if "sw" in name :
		for i in range(0, len(table)):
			printerOnline = table[i].getText()
			
			if name == printerOnline:

				#if this one is idle, then 0 jobs
				if  table[i+1].getText() == "idle\n" :
					jobs = 0
				else:
					#getting number of jobs
					auftrag= table[i+1].find("a").next_sibling 
					try:			
						jobs=re.findall('\d+', auftrag)[0]
						jobs.strip
					except IndexError:
						jobs = 1
#					print(name +",  jobs:" + str(jobs))
				printers.append( tuple( (name, jobs) ) )
				break



		

#Printers and jobs
for (name, jobs) in printers:
	print(name + ", jobs: "+ str(jobs))



min = 5000
the_printer=""
#Finding min
for (name, jobs) in printers:
	if int(min) > int(jobs):
		the_printer=name
		min = jobs
		





#Handling input
copies = "-#1"
for x in sys.argv:
	if re.match("-#\d", x):
               	copies=x

mode = "sides=two-sided-long-edge"
for x in sys.argv:
        if x == "--landscape" or x == "-l":
                mode = "sides=two-sided-short-edge"


for x in sys.argv:
	if not re.match("-.", x):
		file = x

print(file + " to be send to " + the_printer)


#creating the print command
command=["lpr", "-o", mode , copies , "-P", the_printer, file ]
command1="lpr -o " + mode + " " +  copies + " -P " + the_printer + " " + file




#checking for dry input
for x in sys.argv:
	if x == "--dry" or x == "-d":
		print(command1)
		exit(1)



yes = {'yes','y', 'ye', ''}
no = {'no','n'}

print("Are you sure?")


directly_yes=False

for x in sys.argv:
        if x == "--yes" or x == "-y":
                directly_yes=True


if not directly_yes:
	choice = input().lower()
else:
	choice = "yes"


if choice in yes or directly_yes:
	print("Sending print job to " + the_printer + "...") 
	#lpr -o sides=two-sided-long-edge  -#1 -P  $file
	subprocess.run( command )
	
elif choice in no:
   	print(command1)
else:
   sys.stdout.write("Please respond with 'yes' or 'no'")


