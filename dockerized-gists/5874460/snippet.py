import requests
import os, re, sys

RE_SD_VIDEO = re.compile(
  r'<a href="(http://devstreaming.apple.com/videos/wwdc/2013/[^"]*-SD.mov)')
RE_WEBVTT = re.compile(r'fileSequence[0-9]+\.webvtt')

# stdin: dump of https://developer.apple.com/wwdc/videos/
for l in sys.stdin:
	m = RE_SD_VIDEO.search(l)
	if not m:
		continue
	video_url = m.group(1)
	video_dir = video_url[:video_url.rindex('/')]
	session = video_dir[video_dir.rindex('/') + 1:]
	prog_index = requests.get(video_dir + '/subtitles/eng/prog_index.m3u8')

	os.mkdir(session)
	webvtt_names = RE_WEBVTT.findall(prog_index.text)
	for webvtt_name in webvtt_names:
		webvtt = requests.get(video_dir + '/subtitles/eng/' + webvtt_name)
		open(os.path.join(session, webvtt_name), 'w').write(webvtt.text)
