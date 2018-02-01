import re, urllib

htmlSource = urllib.urlopen("https://class.coursera.org/ml/lecture/preview/1").read(200000)
linksList = re.findall('data-lecture-view-link="(.*?)"', htmlSource)

allVideos = []
for link in linksList:
    print 'Open', link
    htmlWithVideo = urllib.urlopen(link).read(200000)
    videosList = re.findall('<source.*type="video/mp4".*? src="(.*?)"',htmlWithVideo)
    print 'Videos:', videosList
    allVideos.extend(videosList)

for video in allVideos:
    print 'Download', video
    fileName = video[video.rfind('/')+1:]
    urllib.urlretrieve(video, fileName)
