###############################
# Script made by @ivanmorenoz #
###############################

# Description: this script uses Pythonista Objc Bridging for unlocking the PDF using PDFKit

from objc_util import ObjCClass, nsurl
from appex import get_file_paths, finish, is_running_extension
from os import remove, path
from console import alert, input_alert, quicklook

def showAlert(msg,file):
	alert(msg, file, "OK", hide_cancel_button=True)
	
def main():

	if not is_running_extension():
		print('This script is intended to be run from the sharing extension.')
		return
		
	files = get_file_paths()
	
	if not files:
		alert('No files were specified')
		return
	
	for file in files:
		filename = path.basename(file)
		
		if not filename.endswith('.pdf'):
			showAlert('Only PDF are allowed', filename)
			continue
	
		pdf = ObjCClass('PDFDocument').alloc().initWithURL(nsurl(file))

		if pdf.isEncrypted():
			pwd = input_alert('Password', filename)
			if pdf.unlockWithPassword_(pwd):
				pdf.writeToFile_(file)
			else:
				showAlert("Wrong Password", filename)
		else:
			showAlert("This PDF is not encrypted", filename)
	finish()

if __name__ == '__main__':
	main()	