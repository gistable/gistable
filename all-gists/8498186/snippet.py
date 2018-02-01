import urllib
import urllib2
try:
	import json
except:
	import simplejson as json
	
# First, Get your API Key for free from: api.animetrics.com
# See at the very below section for HOWTO.
 
# -- Developed by Akatzbreaker (@akatzbreaker) --
 
 
# - (If you discover a Bug, please report by Commenting... Thanks!) -
 
class AnimetricsError(Exception):
	pass

class Animetrics():
	apiKey=''
	imageUrl=''
	detectUrl='http://api.animetrics.com/v1/detect'
	enrollUrl='http://api.animetrics.com/v1/enroll'
	recognizeUrl='http://api.animetrics.com/v1/recognize'
	listGalleriesUrl='http://api.animetrics.com/v1/list_galleries'
	viewGalleryUrl='http://api.animetrics.com/v1/view_gallery'
	viewSubjectUrl='http://api.animetrics.com/v1/view_subject'
	addToGalleryUrl='http://api.animetrics.com/v1/add_to_gallery'
	removeFromGalleryUrl='http://api.animetrics.com/v1/remove_from_gallery'
	deleteFaceUrl='http://api.animetrics.com/v1/delete_face'
	assignFaceUrl='http://api.animetrics.com/v1/assign_face_to_subject'
	
	# Class __init__ Function
	# apiKey: required -> Get your free API Key from api.animetrics.com
	# imageUrl: required
	def __init__(self,apiKey,imageUrl=''):
		self.apiKey=apiKey
		self.imageUrl=imageUrl

	
	# Detect Features of Faces from Image
	# detect() returns
	#	-JSON with Results
	#	-None if status isn't "Complete"
	def detect(self,imageUrl=''):
		if imageUrl=='':
			if self.imageUrl!='':
				imageUrl=self.imageUrl
			else:
				raise AnimetricsError("No Image URL Provided!")
		
		params = urllib.urlencode({'api_key': self.apiKey,'url':imageUrl})
		
		url=self.detectUrl
		req = urllib2.Request(url, params)
		response=json.loads(urllib2.urlopen(req).read())
		if response['images'][0]['status'] == 'Complete':
			return response
		else:
			return None


	# Add Faces to Gallery and give Name/ID for each 
	# enroll() returns:
	#	-True: all faces enrolled
	#	-False: no faces Detected
	#	-Raises in the End AnimetricsError if an error Occures. Doesn't stop flow...
	def enroll(self,imageUrl='',subjectName='',galleryid='gallery1'): # subjectName will apply only if 1 face is detected!
		if imageUrl=='':
			if self.imageUrl!='':
				imageUrl=self.imageUrl
			else:
				raise AnimetricsError("No Image URL Provided!")
		
		detectionResults=self.detect(imageUrl)
		errors={}
		no=0
		if len(detectionResults['images'][0]['faces']) == 0:
			return False
			
		for face in detectionResults['images'][0]['faces']:
			no+=1
			if len(detectionResults['images'][0]['faces']) != 1 or subjectName == '':
				subject_name=raw_input("Enter Name for Subject " + str(no) + ": ")		
			else:
				subject_name=subjectName
				
			if galleryid=='':
				galleryid='gallery1'
			
			params = urllib.urlencode({
				'api_key': self.apiKey,
				'gallery_id':galleryid,
				'image_id':detectionResults['images'][0]['image_id'],
				'width':detectionResults['images'][0]['width'],
				'height':detectionResults['images'][0]['height'],
				'subject_id':subject_name,
				'topLeftX':face['topLeftX'],
				'topLeftY':face['topLeftY']
				}
			)	
			url=self.enrollUrl
			try:
				req = url + "?" + params
				response=json.loads(urllib2.urlopen(req).read())
			except Exception,e:
				errors[subject_name]=str(e)
		
		if errors == {}:
			return True
		else:
			raise AnimetricsError("Error Encountered while Enrolling:\n" + "\n".join(x + "-> " + errors[x] for x in errors.keys()) + "\n	All the Others Enrolled Successfully!")


	# Recognize Face from Gallery (must be enrolled)
	# recognize() returns:
	#	- dictionary (keys=Names,values=Probabilities)
	#	- str with status  if it isn't "Complete"
	#	- None if no Faces Detected
	def recognize(self,imageUrl=''):
		if imageUrl=='':
			if self.imageUrl!='':
				imageUrl=self.imageUrl
			else:
				raise AnimetricsError("No Image URL Provided!")
		detectionResults=self.detect(imageUrl)
		
		if len(detectionResults['images'][0]['faces']) == 0:
			return None
			
		params = urllib.urlencode({
				'api_key': self.apiKey,
				'gallery_id':"gallery1",
				'image_id':detectionResults['images'][0]['image_id'],
				'width':detectionResults['images'][0]['width'],
				'height':detectionResults['images'][0]['height'],
				'topLeftX':detectionResults['images'][0]['faces'][0]['topLeftX'],
				'topLeftY':detectionResults['images'][0]['faces'][0]['topLeftY']
				})
		
		url=self.recognizeUrl + "?" + params
		response=json.loads(urllib2.urlopen(url).read())
		if response['images'][0]['transaction']['status'] == 'Complete':
			return response['images'][0]['candidates']
		else:
			return response['images'][0]['transaction']['status']


	# List all Galleries
	# listGalleries() returns:
	#	- list with Gallery Names/IDs if successful
	#	- None if not Successful
	def listGalleries(self):
		params = urllib.urlencode({
			"api_key":self.apiKey
		})
		url=self.listGalleriesUrl + "?" + params
		r=json.loads(urllib2.urlopen(url).read())
		if r['status'] == 'Complete':
			return r['gallery_ids']
		else:
			return None
	
			
	# Get Subject Names from Gallery
	# viewGallery returns():
	#	- dictionary (keys=Gallery ID, values=list with Subject Names/IDs)
	def viewGallery(self,galleryid=''): # If 'galleryid' is empty, all galleries will be checked
		ids=[]
		if galleryid=='':
			ids=self.listGalleries()
		else:
			ids=[galleryid]
		galls={}	
		for id in ids:
			galls[id]=[]
			galls[id].extend(
				json.loads(
					urllib2.urlopen(
							self.viewGalleryUrl + "?" + urllib.urlencode(
								{"api_key":self.apiKey,'gallery_id':id})
						).read()
					)['subject_ids'])
				
		return galls
		
		
	# Get Subject Face IDs Enrolled
	# viewSubject returns():
	#	- list with all Face IDs enrolled if successful
	#	- None if not Successful
	def viewSubject(self,subjectid): # 'subjectid' is required!
		ids=[]
		if subjectid=='':
			raise AnimetricsError("No subjectid Given!")
		url=self.viewSubjectUrl + "?"  + urllib.urlencode({"api_key":self.apiKey,'subject_id':subjectid})
		r=json.loads(urllib2.urlopen(url).read())
		if r['status'] == "Complete":
			return r['face_ids']
		else:
			return None

		
	# Add already enrolled Subject to a Gallery by ID.
	# addToGallery() returns:
	#	- True if successful
	#	- False if unsuccessful
	def addToGallery(self,subjectid,galleryid): # Both Parameters are Required // If galleryid doesn't exist, it will be created
		url=self.addToGalleryUrl + "?" + urllib.urlencode({'api_key':self.apiKey,'subject_id':subjectid,'gallery_id':galleryid})
		r=json.loads(urllib2.urlopen(url).read())
		if r['status'] == 'Complete':
			return True
		else:
			return False

			
	# Remove Subject from a Gallery by ID. / If subject in no Gallery, it will be deleted from the Face Recognition System
	# removeFromGallery() returns:
	#	- True if successful
	#	- False if unsuccessful
	def removeFromGallery(self,subjectid,galleryid): # Both Parameters are Required // If galleryid doesn't exist, it will be created
		url=self.removeFromGalleryUrl + "?" + urllib.urlencode({'api_key':self.apiKey,'subject_id':subjectid,'gallery_id':galleryid})
		r=json.loads(urllib2.urlopen(url).read())
		if r['status'] == 'Complete':
			return True
		else:
			return False
	
	
	# Delete Face from a Subject by ID.
	# deteleFace() returns:
	#	- True if successful
	#	- False if unsuccessful
	def deleteFace(self,faceid): # 'faceid' is required
		url=self.deleteFaceUrl + "?" + urllib.urlencode({'api_key':self.apiKey,'face_id':faceid})
		r=json.loads(urllib2.urlopen(url).read())
		if r['status'] == 'Complete':
			return True
		else:
			return False
		
			
	# Assign Face to a Subject by ID.
	# assignFace() returns:
	#	- True if successful
	#	- False if unsuccessful
	def assignFace(self,faceid,subjectid): # Both Parameters are Required
		url=self.assignFaceUrl + "?" + urllib.urlencode({'api_key':self.apiKey,'face_id':faceid,'subject_id':subjectid})
		r=json.loads(urllib2.urlopen(url).read())
		if r['status'] == 'Complete':
			return True
		else:
			return False
			
			
## HOW TO USE QUICK GUIDE: ##
"""
api_key='YOUR_API_KEY_HERE' # Get your Key from api.animetrics.com (it's free!)

a=Animetrics(api_key)

a.enroll('http://www.stars-arena.com/wp-content/uploads/2013/08/Tom-Cruise-looks.jpg','tom cruise')
a.enroll('http://awiderbridge.org/staging/wp-content/uploads/2013/11/tom-cruise-playboy-interview-660.jpg','tom cruise')

a.enroll('http://www.biography.com/imported/images/Biography/Images/Profiles/O/Barack-Obama-12782369-2-402.jpg','barack obama')
a.enroll('http://upload.wikimedia.org/wikipedia/commons/e/e9/Official_portrait_of_Barack_Obama.jpg','barack obama')

a.recognize('http://grassrootjournal.com/wp-content/uploads/2013/10/121204_barack_obama_ap_605.jpg')
a.recognize('http://www.stars-arena.com/wp-content/uploads/2013/08/Tom-Cruise-with-short-hairs.jpg')

# Before Each Class Function, it is commented:
# what each function does, what it returns on each condition.

...::ENJOY::...
		-akatzbreaker
"""

