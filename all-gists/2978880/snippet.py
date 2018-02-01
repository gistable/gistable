import urllib
import re
 
#The output HTML file to which the list of URLs will be written.
#The list of URLs are written as anchor links.
#Open this page and use your favorite download manager to download
#all the videos. I use Firefox/FlashGot combo with Free Download
#Manager.
outputhtml = open('ml.html' ,'w')
 
#The contents of the "course preview" page of a particular course is stored.
#The "course preview" page has URL of the form similar to one given below 
#for "Probabilistic Graphical Models" course.
mainpage = urllib.urlopen("https://class.coursera.org/ml/lecture/preview");
mainpage_contents = mainpage.read()
 
#An example link to a course video within the index page would be:
#https://class.coursera.org/pgm/lecture/preview_view?lecture_id=17
#So, we use regex to find all similar URLs.
allvideos = re.findall('"([^"]*?lecture_id[^"]*?) "',mainpage_contents)
 
#Now, for each URL found
for vid in allvideos:
    #Read that particular video's page
    vidcontent = urllib.urlopen(vid).read()
 
    #Find the title of the video from the page. If title not found, something is wrong, so
    #forget the current video URL and continue with the next URL,
    vidtitle = re.findall('<div id="lecture_title" class="hidden">(.*?)</div>',vidcontent)
    if (len(vidtitle) > 0):
        vidtitle = vidtitle[0]
    else:
        continue
 
    #Find the link to mp4 file in the page. Again, if such a URL is not found, then something
    #is wrong, so skip the current page.
    vidurl = re.findall('"([^"]*?\.mp4)"', vidcontent)
    if (len(vidurl) > 0):
        vidurl = '<a href="' + vidurl[0] + '">' + vidtitle + '</a>'
    else:
        continue
 
    #We also find the subtitle to the current video. You can see "_en" in the regex, which
    #corresponds to the english subtitles. You can replace it with your language, but see
    #first if Coursera supports it.
    #If we don't find a subtitle, then no worries. That video may not have one.
    vidsub = re.findall('"([^"]*?_en)"', vidcontent)
    if (len(vidsub) > 0):
        vidsub = '<a href="' + vidsub[0] + '">Subtitle</a>'
    else:
        vidsub = ''
 
    #Write the URLs to the HTML file.
    outputhtml.write(vidurl + ' ' + vidsub + '\n')
 
    #Print the video title to the console so that the user can get feedback on which URLs have
    #been successfully processed.
    print vidtitle
 
outputhtml.close()