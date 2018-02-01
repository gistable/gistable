__author__ = 'Eslam Hamouda | eslamx.com'


import configparser
import os.path
import json
import io

# get the required files paths to access Firefox AppData
win_user_profile = os.getenv('USERPROFILE')
ff_path = r'{0}\AppData\Roaming\Mozilla\Firefox'.format(win_user_profile)
ini_path = "{0}\\profiles.ini".format(ff_path)


# check if the INI configuration file exists to continue or not
if not os.path.exists(ini_path):
    print("*** Firefox is not installed or not recognized by this script ***")
    exit(0)

# parsing the INI file and extract firefox user profile folder name and create the full path
profiles = configparser.ConfigParser()
profiles.read(ini_path)
current_profile_dir = profiles['Profile0']['Path']
current_profile_path = "{0}\\{1}".format(ff_path,str(current_profile_dir).replace('/','\\'))

# append the downloads.json file to the full path
downloads_path = current_profile_path + "\\downloads.json"

# check if the downloads.json file exists or not because FireFox automatically removes it if it was empty.
if not os.path.exists(downloads_path):
    print("*** You don't have any broken downloads ***")
else:
    # read the json file and parse it
    json_file = open(downloads_path,mode='r+')
    js = json.load(json_file)
    json_file.close()

    # a double check for having a paused Downloads
    if len(js['list']) == 0:
        print("*** You don't have any broken downloads ***")
        exit(0)

    print("\n\n**** Current Paused Firefox Downlaods **** \n")
    
    # print the current list of paused downloads
    item_number = 1
    for download_item in js['list']:
        # extract the short file name from the file full path
        fname = str(download_item['target']['path']).split('\\')[-1:][0]
        # get the file URL
        furl = download_item['source']
        # sometimes Firefox saves the file URL inside another object with the referrer URL too if it wasn't a direct link.
        if type(furl) is dict and download_item['source']['url'] is not None:
            furl = download_item['source']['url']
        # some stupid prints with awful formating 
        print("#{0} : Filename : {1} \n\t URL : {2}\n\t Path : {3} \n\t Size : {4} \n\t Resumable : {5}".format(item_number,
                                                                                                                fname,
                                                                                                                furl,
                                                                                                                download_item['target']['path'],
                                                                                                                str(round((download_item['totalBytes']/1024)/1024,2)) + " MB",
                                                                                                                download_item['hasPartialData']
                                                                                                                ))
        # items counter
        item_number += 1
    # take the user inputs to update the json file
    file_number = input("\nEnter the file number to Edit the URL with the new one :")
    file_new_url = input("\nEnter the new URL :")
    #update the json object
    js['list'][int(file_number) - 1]['source'] = file_new_url
    # write the json object into the downloads.json file with updated values.
    json_file = open(downloads_path,mode='w')
    json.dump(js,json_file,ensure_ascii=False)
    json_file.close()

print("*** URL has been updated | you need to restart Firefox to see the changes ***")
print("After restart you can resume the file from Firefox Downloads window ;)")
exit(0)
# now you are happy with your resumable download ;)