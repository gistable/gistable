#!/usr/bin/env python3

import requests as rq
from bs4 import BeautifulSoup as BS
import time
import sys

students_list = []

results_form_url="http://results.rvce.edu.in/"
results_url="http://results.rvce.edu.in/viewresult2.php"

print("Enter [YEAR] [DEPT CODE] [RANGE]")
print("Example: 16 cs 1-100")
print("For results 1rv16cs001 to 1rv16cs100")
year,dept_code,rang = input().split()
base_usn="1rv"+year+dept_code.lower()
range_start,range_end = rang.split('-')
usn_list=[base_usn+"%03d"%i for i in range(int(range_start),int(range_end)+1)]
print("Output File Name: [Press Enter for default name {}.txt]".format(base_usn))
op_file_name = input()

#solve one captcha to get valid session
s=rq.session()
r=s.get(results_form_url)
soup = BS(r.content, "html.parser")
captcha = soup.find_all("label")[1].text
captcha_answer = int(captcha[8])+int(captcha[12])


class Student(object):
    def __init__(self,programme,usn,name,semester,sgpa):
        self.programme=programme
        self.usn=usn
        self.name=name
        self.semester=semester
        self.sgpa=sgpa
        self.grades={}
    def __str__(self):
        res = "Programme: "+self.programme+"\n"
        res += "USN: "+self.usn+"\n"
        res += "Name: "+self.name+"\n"
        res += "Semester: "+self.semester+"\n"
        res += "SGPA: "+self.sgpa+"\n"
        res += "Grades: "+str(self.grades)+"\n"
        return res
    def __repr__(self):
        return self.__str__()

def getResult(usn):
    params = {
        "usn":usn,
        "captcha":captcha_answer,
    }
    response = s.post(results_url, data=params)
    result_soup = BS(response.content,"html.parser")
    if(result_soup.find("div", {"id":"no-more-tables"})==None):
        print("USN "+usn+" doesn't exist")
        return None
    tables = result_soup.find_all('tbody')
    #print(tables[1].prettify())
    student_details = tables[0].tr.find_all("td")
    student_courses = tables[1].find_all("tr")
    new_student = Student(*[x.text for x in student_details])
    for c in student_courses:
        course_data = [t.text for t in c.find_all("td")]
        if(course_data[0]!=''):
            new_student.grades[course_data[0]]=course_data[2]
    students_list.append(new_student)
    return new_student

def printProgress(i, n):
    #index from 1 instead of 0
    i+=1
    percent = float(i)*100/n
    sys.stdout.write("\rGetting result {0}/{1} [{2:.2f}%]".format(i,n,percent))


time_start = time.time()

for i in range(len(usn_list)):
    getResult(usn_list[i])
    printProgress(i, len(usn_list));
    #new = getResult(usn)
    #if new!=None:
    #    students_list.append(new)
time_end = time.time()
print("\n")
print("Time: {0:.2f}".format(time_end-time_start))
if(op_file_name==""):
    f = open("results_"+base_usn+".txt","w+")
else:
    f = open(op_file_name,"w+")
for s in students_list:
    f.write(str(s)+'\n')
