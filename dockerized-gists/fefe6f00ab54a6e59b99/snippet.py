import sys
import requests
import json
import time
import re
import base64

class NvidiaDriverGrabber():
	def __init__(self, lookup_url, process_url, product_types, locale, language, throttle = 5):
		self.LOOKUP_URL = lookup_url
		self.PROCESS_URL = process_url
		self.PRODUCT_TYPES = product_types
		self.locale = locale
		self.language = language
		self.start_time = time.time()
		self.end_time = None
		self.output = {'_meta': {'created_by': 'NVIDIA Driver Grabber.py v1.2', 'created_on': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}}
		self.errors = []
		self.throttle = throttle


	def lookup_request(self, step, value):
		args = "?TypeID={}&ParentID={}".format(step, value)
		print "--> " + self.LOOKUP_URL + args
		r = None
		try:
			r = requests.get(self.LOOKUP_URL + args)
		except Exception:
			time.sleep(80)
			r = requests.get(self.LOOKUP_URL + args)
		r.close()
		print r.content
		print r.status_code
		return r.text


	def process_request(self, ProductSeriesID, ProductFamilyID, RPF, OperatingSystemID, LanguageID, Locale, CUDAToolkit):
		args = "?psid={}&pfid={}&rpf={}&osid={}&lid={}&lang={}&ctk={}" \
				.format(ProductSeriesID, ProductFamilyID, RPF, OperatingSystemID, LanguageID, Locale, CUDAToolkit)
		print "==> " + self.PROCESS_URL + args
		r = None
		try:
			r = requests.get(self.PROCESS_URL + args)
		except Exception:
			time.sleep(80)
			r = requests.get(self.LOOKUP_URL + args)
		r.close()
		print r.content
		print r.status_code
		return r.text


	def step1(self):
		self.output["product_types"] = {}
		for model in self.PRODUCT_TYPES:
			self.output["product_types"][model["name"]] = {}
		return self.output


	# get ProductSeriesID
	def step2(self):
		for ptype in self.PRODUCT_TYPES:
			request = self.lookup_request('2', ptype["value"])
			m = re.findall(r'\<LookupValue RequiresProduct="(\w+)" ParentID="(\d+)"\>\n<Name>(.*)</Name>\n<Value>(.*)</Value>', request.replace("\r", "\n"))
			if not m:
				sys.stderr.write("step2(): Regex match failed for {}.\n".format(ptype["name"]))
				self.errors.append("step2(): Regex match failed for {}.\n".format(ptype["name"]))
				continue
				#raise Exception("Failed to find a regex match for an iteration")
			for match in map(list, m):
				m_RequiresProduct = match[0] == "True"
				m_ParentID = match[1]
				m_SeriesName = match[2]
				m_SeriesID = match[3]
				self.output["product_types"][ptype["name"]][m_SeriesName] = \
				{
					"_meta": {
						"ProductTypeID": ptype["value"],
						"ProductSeriesID": m_SeriesID,
						"ProductSeriesName": m_SeriesName,
						"SubProducts": m_RequiresProduct
					}
				};
			time.sleep(self.throttle)
		return self.output


	# get ProductFamilyID
	def step3(self):
		for ptype in self.PRODUCT_TYPES:
			for Series in self.output["product_types"][ptype["name"]]:
				series = self.output["product_types"][ptype["name"]][Series]
				#if series["_meta"]["SubProducts"] == False:
				#	continue
				print series
				request = self.lookup_request('3', series['_meta']["ProductSeriesID"])
				m = re.findall(r'\<LookupValue ParentID="(\d+)"\>\n<Name>(.*)</Name>\n<Value>(.*)</Value>', request.replace("\r", "\n"))
				if not m:
					sys.stderr.write("step3(): Regex match failed for {}.\n".format(series))
					self.errors.append("step3(): Regex match failed for {}.\n".format(series))
					continue
					#raise Exception("Failed to find a regex match for an iteration")
				for match in map(list, m):
					m_ParentID = match[0]
					m_ProductName = match[1]
					m_ProductID = match[2]
					self.output["product_types"][ptype["name"]][series["_meta"]["ProductSeriesName"]][m_ProductName] = \
					{
						"_meta": {
							"ProductID": m_ProductID,
							"ProductName": m_ProductName
						}
					};
				time.sleep(self.throttle)
		return self.output


	# get OSID
	def step4(self):
		for ptype in self.PRODUCT_TYPES:
			for Series in self.output["product_types"][ptype["name"]]:
				if Series == "_meta":
					continue
				series = self.output["product_types"][ptype["name"]][Series]
				request = self.lookup_request('4', series['_meta']["ProductSeriesID"])
				m = re.findall(r'\<LookupValue Code="(.*)"\>\n<Name>(.*)</Name>\n<Value>(.*)</Value>', request.replace("\r", "\n"))
				if not m:
					sys.stderr.write("step4(): Regex match failed for {}.\n".format(Series))
					self.errors.append("step4(): Regex match failed for {}.\n".format(Series))
					continue
					#raise Exception("Failed to find a regex match for an iteration")
				for products in series:
					if products == "_meta":
						continue
					product = series[products]
					for match in map(list, m):
						m_OSCode = match[0]
						m_OSName = match[1]
						m_OSID = match[2]
						self.output["product_types"][ptype["name"]][series["_meta"]["ProductSeriesName"]][product["_meta"]["ProductName"]][m_OSName] = \
						{
							"_meta": {
								"OSCode": m_OSCode,
								"OSName": m_OSName,
								"OSID": m_OSID
							}
						};
				time.sleep(self.throttle)
		return self.output


	# Finish up and make a PROCESS request
	def step5(self):
		for ptype in self.PRODUCT_TYPES:
			for Series in self.output["product_types"][ptype["name"]]:
				if Series == "_meta":
					continue
				series = self.output["product_types"][ptype["name"]][Series]
				for products in series:
					if products == "_meta":
						continue
					product = series[products]
					for OS in product:
						if OS == "_meta":
							continue
						os = product[OS]
						p = self.output["product_types"][ptype["name"]][series["_meta"]["ProductSeriesName"]][product["_meta"]["ProductName"]]
						#ProductSeriesID, ProductFamilyID, RPF, OperatingSystemID, LanguageID, Locale, CUDAToolkit
						ProductSeriesID = series["_meta"]["ProductSeriesID"]
						ProductFamilyID = product["_meta"]["ProductID"]
						RPF = 1
						OperatingSystemID = os["_meta"]["OSID"]
						LanguageID = self.language
						Locale = self.locale
						CUDAToolkit = 0
						r = self.process_request(ProductSeriesID, ProductFamilyID, RPF, OperatingSystemID, LanguageID, Locale, CUDAToolkit)
						if r[0] == "<":
							p[OS]["DriverDownload"] = False
						else:
							p[OS]["DriverDownload"] = r
						time.sleep(self.throttle)

		self.end_time = time.time()
		self.time_elapsed = self.end_time - self.start_time;
		self.output["_meta"]["time_elapsed"] = self.time_elapsed
		if len(self.errors) > 0:
			print "============ ERRORS ============"
			print self.errors
		self.output["_meta"]["errors"] = self.errors
		return self.output

		

PRODUCT_TYPES = [
	{
		"value": 1,
		"name": "GeForce"
	},
	{
		"value": 3,
		"name": "Quadro"
	},
	{
		"value": 8,
		"name": "NVS"
	},
	{
		"value": 7,
		"name": "Tesla"
	},
	{
		"value": 9,
		"name": "GRID"
	},
	{
		"value": 5,
		"name": "3D Vision"
	},
	#{
	#	"value": 2,
	#	"name": "nForce"
	#},
	{
		"value": 6,
		"name": "ION"
	},
	{
		"value": 4,
		"name": "Legacy"
	}
]

def write_to_file(file_name, contents):
	FileWriter = open(file_name, 'w')
	data = json.dumps(contents)
	FileWriter.write(data)

DriverSearch = NvidiaDriverGrabber("http://www.nvidia.com/Download/API/lookupValueSearch.aspx", "http://www.nvidia.com/Download/processDriver.aspx", PRODUCT_TYPES, "en-us", 1)
Step1 = DriverSearch.step1()
print Step1
write_to_file("step1.txt", Step1)
Step2 = DriverSearch.step2()
print Step2
write_to_file("step2.txt", Step2)
Step3 = DriverSearch.step3()
print Step3
write_to_file("step3.txt", Step3)
Step4 = DriverSearch.step4()
print Step4
write_to_file("step4.txt", Step4)
Step5 = DriverSearch.step5()
print Step5
write_to_file("step5.txt", Step5)
print "Done!"