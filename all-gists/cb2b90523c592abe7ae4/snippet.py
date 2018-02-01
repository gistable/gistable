#! /usr/bin/env python

from sqlalchemy import *
from sqlalchemy.sql import select
from ps_db_utils import *
import csv
import os
import shutil
from datetime import *


class StudentData(object):

	def __init__(self):
		self.fields_for_moodle = [
			'id',
			'dcid',
			'my_custom_field1',
			'student_number',
			'first_name',
			'last_name',
			'city',
			'schoolid',
			'grade_level',
			'graduation_year',
			'my_custom_field2',
		]
		self.minimum_grade_level = 2
		self.maximum_grade_level = 99
		
		self.db = PsDB()
		
		self.table = self.db.reverse_table("students")
		self.table_fields = self.table.c.keys()
		
		self.custom_fields = None
		self.custom_fields_table = None
		if "u_studentsuserfields" not in self.db.meta.tables.keys():
			self.custom_fields_table = Table("u_studentsuserfields", self.db.meta,
				Column('studentsdcid', String(50), primary_key=True),
				Column('studentsdcid', Integer, ForeignKey("students.dcid"), primary_key=True),
				autoload=True)
		else:
			self.custom_fields_table = self.db.meta.tables["u_studentsuserfields"]

		if self.custom_fields_table != None:
			self.custom_fields = self.custom_fields_table.c.keys()


def get_field(main_row, custom_row, student_data, field_name):
	if field_name in student_data.table_fields:
		return main_row.__dict__[field_name]
	elif field_name in student_data.custom_fields:
		return custom_row.__dict__[field_name]
	return None

def valid_student(row, student_data):
	enrolled = False
	valid_grade = False

	# Is student enrolled or pre-enrolled and with a start date in the next 5 days?
	# "0" is active (False boolean value), anything else is inactive.
	# "-1"
	if row.enroll_status == 0:
		enrolled = True
	if row.enroll_status == -1 and row.entrydate:
		# Parse entrydate, and make it three days earlier
		#entry_date = datetime.strptime(row.entrydate[0:10],"%Y-%m-%d") + timedelta(days=-3)
		entry_date = row.entrydate + timedelta(days=-14)
		print "Found pre-registered! dcid %s, entry_date %s" % (row.dcid, entry_date, )
		if entry_date < datetime.now():
			enrolled = True

	# Check grade level, if enroll_status is ok!
	if row.grade_level >= student_data.minimum_grade_level and row.grade_level <= student_data.maximum_grade_level:
		valid_grade = True
	else:
		valid_grade = False

	return enrolled and valid_grade


def ps_fullexport_students():

	print "PowerSchool Export of Students data started."

	db = PsDB()

	student_data = StudentData()

	header = []
	for field in student_data.fields_for_moodle:
		header.append(field)

	correct_students_file_name = "ps_students.csv"
	print "Writing data to files %s" % correct_students_file_name

	correct_students_file = open(correct_students_file_name, 'wb')
	correct_students_writer = csv.writer(correct_students_file,dialect='excel')
	correct_students_writer.writerow(header)

	print "Header written to files."

	count = 0

	main_student_data = db.get_session().query(student_data.table).all()
	custom_student_data = db.get_session().query(student_data.custom_fields_table).all()
	for row in main_student_data:
		# Full Dump Line
		line = []
		# Student specific restriction!!! "0" is active (False boolean value), anything else is inactive.
		if valid_student(row, student_data):
			for cf in custom_student_data:
				if row.dcid == cf.studentsdcid:
					for field in student_data.fields_for_moodle:
						line.append( get_field(row, cf, student_data, field) )

					if line:
						writer = correct_students_writer
						count = count + 1
						writer.writerow(line)
						if count % 50 == 0:
							print "Exported %s records." % count

	correct_students_file.close()
	print "Finished. Exported %s records in total." % count

if __name__ == "__main__":
	ps_fullexport_students()
