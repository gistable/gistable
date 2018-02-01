#! /usr/bin/python

def downloadFileWithProgress(url, downloadFolder='./', sha1=None, chunk_size=8192):
  import requests, sys
  """
  Function to download a file from the specified URL.
  Outputs a basic progress bar and download stats to the CLI.

  Optionally downloads to a specified download folder, and checks the SHA1 checksum of the file.
  Chunk size can also be specified, to control the download.

  Uses 'Requests' :: http://www.python-requests.org
  """
  def size_fmt(numBytes):
    for symbol in ['B','KB','MB','GB','TB','EB','ZB']:
      if numBytes < 1024.0:
        return "{0:3.1f} {1}".format(numBytes, symbol)
      else:
        numBytes /= 1024.0
    # Return Yottabytes if all else fails.
    return "{0:3.1f} {1}".format(numBytes, 'YB')

  local_file = downloadFolder + '/' + url.split('/')[-1]

  r = requests.get(url, stream=True)
  r.raise_for_status()

  file_size = int(r.headers['Content-Length'])
  dl_size = 0

  print "Downloading: {0}; {1}".format(local_file.split('/')[-1], size_fmt(file_size))
  with open(local_file, 'wb') as f:
    for chunk in r.iter_content(chunk_size):
      if chunk: # filter out keep-alive new chunks
        dl_size += len(chunk)
        f.write(chunk)
        f.flush()
        percentage = (dl_size * 100. / file_size)
        num_equals = int(round(percentage/4))

        sys.stdout.write("[{0:25}] {1:>10} [{2: 3.2f}%]\r".format('='*num_equals, size_fmt(dl_size), percentage))
        sys.stdout.flush()
  print
  if sha1 is not None:
    import hashlib
    print("Verifying download...")
    f = open(local_file, 'rb')
    download_checksum = hashlib.sha1(f.read()).hexdigest()
    f.close()
    if download_checksum == sha1:
      return local_file
    else:
      raise Exception("Checksum mismatch")
  else:
    return local_file

# Example usage, with SHA1 verification:
downloadFileWithProgress('http://support.apple.com/downloads/DL1755/en_US/OSXUpdCombo10.9.4.dmg', sha1='3c02ee0c3e2aa11831547571dd6fa502130ee5d6')
