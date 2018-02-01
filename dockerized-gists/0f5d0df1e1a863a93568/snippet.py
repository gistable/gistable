# UdacityDownload.py
# Python 2.7.6

"""
Python script to download course content from udacity courses
- Creates folders as per course names
- Downloads all the zip files
- Extract content from zip file
- Finally delete the zip file
Multiple course content can be downloaded from list
"""

import requests
from BeautifulSoup import BeautifulSoup
import zipfile
import os

# Parent directory under which all content to be downloaded
# ../../ notation will take 3 levels up
base_dir = "../../Vinoth/MOOC/Udacity/"

# Udacity id of the courses of interest
# Configure this list to download multiple course content
# course_lst = ["ud617", "ud359"]
course_lst = ["ud675", "ud741", "ud820"]

# Dict to map course id with course name
courses = dict()

# The catalog page lists out all courses available for download
# Use this page to extract course name from course id
catalog_url = "https://www.udacity.com/wiki/downloads"

catalog_resp = requests.get(catalog_url)

catalog_soup = BeautifulSoup(catalog_resp.content)

lis = catalog_soup.findAll("li")
for li in lis:
    for a in li("a"):
        # case insensitive comparison
        if a.getText().lower() in [course.lower() for course in course_lst]:
            courses[a.getText()] = li.getText()

for course_id in courses:

    print("***Downloading {}".format(courses[course_id]))

    # Construct the path to download content, and strip unwanted characters
    download_dir = os.path.join(base_dir, courses[course_id].replace(":", ""))
    print download_dir

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # ud359 is the id for "Intro to Data Science" course
    # Full download catalog - https://www.udacity.com/wiki/downloads
    course_url = "https://www.udacity.com/wiki/" + course_id + "/downloads"

    resp = requests.get(course_url)

    print("Opening url {}".format(course_url))

    soup = BeautifulSoup(resp.content)

    # Video links are within a <li> tag
    lis = soup.findAll("li")

    for li in lis:
        for a in li("a"):
            # Filter for zip files
            if(a.get("href").split(".")[-1] == "zip"):
                link = a.get("href")  # Video download link
                name = a.getText()  # Name of file
                print ("{}: {}".format(name, link))

                vresp = requests.get(link)

                with open(os.path.join(download_dir, name), "wb") as video:
                    for chunk in vresp.iter_content(chunk_size=1024):
                        if chunk:
                            video.write(chunk)
                print("Video zip files downloaded in {}".format(
                    os.path.join(download_dir, name)))

                # Unzip the file and save in current location
                try:
                    with zipfile.ZipFile(
                            os.path.join(download_dir, name), "r") as zfile:
                        # Save the extracted file under a folder with same name
                        # .zip extension is striped out get folder name
                        zfile.extractall(
                            os.path.join(download_dir, name.split(".")[0]))
                    print("Zip file extracted")
                except Exception as e:
                    print (e)
                    continue

                # After extraction remove original zip file
                try:
                    os.remove(os.path.join(download_dir, name))
                    print("Zip file deleted")
                except Exception as e:
                    print (e)
                    continue
