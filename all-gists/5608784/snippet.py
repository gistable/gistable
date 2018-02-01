#!/usr/bin/python

def poorMansConvert(di, inPath, outType, outPath):
  from apiclient.http import MediaFileUpload

	valid_output = [
		'text/html','text/plain','application/rtf','application/vnd.oasis.opendocument.text',\
		'application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document',\
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/x-vnd.oasis.opendocument.spreadsheet',\
		'image/jpeg','image/png','image/svg+xml','application/vnd.openxmlformats-officedocument.presentationml.presentation'	
	]
	
	if outType not in valid_output:
		raise Exception("Out type not valid, use one of the following: %s" % ','.join(valid_output))
	
	media_body = MediaFileUpload(inPath,resumable=True)
	drive_file = di.files().insert(media_body=media_body, convert=True).execute()
	file_id = drive_file['id']	
	if drive_file['exportLinks'].has_key(outType):
		download_url = drive_file['exportLinks'][outType]
		resp, content = di._http.request(download_url)
	
		if resp.status == 200:
			f = open(outPath,"w")
			f.write(content)
			f.close()
		else:
			raise Exception("Failed to download file: %s" % resp)
		
		di.files().trash(fileId=file_id).execute()
	else:
		raise Exception("Output file type not compatible with input file, use one of the following: %s" % ','.join(drive_file['exportLinks'].keys()))
		
	return content