from pydrive.auth import GoogleAuth  
from pydrive.drive import GoogleDrive    

"""API calls to download a very large google drive file.  The drive API only allows downloading to ram 
   (unlike, say, the Requests library's streaming option) so the files has to be partially downloaded
   and chunked.  Authentication requires a google api key, and a local download of client_secrets.json

   Thanks to Radek for the key functions: http://stackoverflow.com/questions/27617258/memoryerror-how-to-download-large-file-via-google-drive-sdk-using-python
"""

def partial(total_byte_len, part_size_limit):
    s = []
    for p in range(0, total_byte_len, part_size_limit):
        last = min(total_byte_len - 1, p + part_size_limit - 1)
        s.append([p, last])
    return s

def GD_download_file(service, file_id):
  drive_file = service.files().get(fileId=file_id).execute()
  download_url = drive_file.get('downloadUrl')
  total_size = int(drive_file.get('fileSize'))
  s = partial(total_size, 100000000) # I'm downloading BIG files, so 100M chunk size is fine for me
  title = drive_file.get('title')
  originalFilename = drive_file.get('originalFilename')
  filename = './' + originalFilename
  if download_url:
      with open(filename, 'wb') as file:
        print "Bytes downloaded: "
        for bytes in s:
          headers = {"Range" : 'bytes=%s-%s' % (bytes[0], bytes[1])}
          resp, content = service._http.request(download_url, headers=headers)
          if resp.status == 206 :
                file.write(content)
                file.flush()
          else:
            print 'An error occurred: %s' % resp
            return None
          print str(bytes[1])+"..."
      return title, filename
  else:
    return None          
            

gauth = GoogleAuth()
gauth.CommandLineAuth() #requires cut and paste from a browser 
 
FILE_ID = 'SOMEID' #FileID is the simple file hash, like 0B1NzlxZ5RpdKS0NOS0x0Ym9kR0U

drive = GoogleDrive(gauth)
service = gauth.service
#file = drive.CreateFile({'id':FILE_ID})    # Use this to get file metadata
GD_download_file(service, FILE_ID) 
