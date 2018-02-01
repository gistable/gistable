import os
import glob
import exifread

NAME_LENGTH = 10

jpg_files = glob.glob('*.jpg')

for a_file in jpg_files:
    try:
        tags = exifread.process_file(open(a_file, 'rb'))
    except Exception as e:
        print(e)
        print("Couldn't open the file, skipping: {}".format(a_file))
        continue
    uid = str(tags.get('EXIF ImageUniqueID', ''))
    if not len(uid):
        print("{} --> UniqueID not present in EXIF".format(a_file))
    elif len(uid) < 30:
        print("{} --> Possibly corrupted EXIF; {}".format(a_file, uid))
    else:
        new_name = uid[:NAME_LENGTH] + '.jpg'
        print("{} --> new name: {}".format(a_file, new_name))