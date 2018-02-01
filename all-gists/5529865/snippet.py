file_save_dir = 'images'
filename_length = 20
filename_charset = string.ascii_letters + string.digits

linestring = open('Google Image Search.html').read()
for match in re.findall(r'imgurl=(.*?(?:&|\.(?:jpg|gif|png|jpeg)))', linestring, re.I):
  print match

  try:
    filename = ''.join(random.choice(filename_charset)
                     for s in range(filename_length))
    urllib.urlretrieve (match,
                      os.path.join(file_save_dir, filename + '.jpg'))
  except:
    print "unable to open url " + match