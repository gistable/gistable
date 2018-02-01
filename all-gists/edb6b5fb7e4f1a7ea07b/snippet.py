'''
Sample usage:
python ytwebm.py https://www.youtube.com/watch?v=dQw4w9WgXcQ -s 01:45 -l 5
This will create webm file from youtube video from 01:45 to 01:50
'''

import youtube_dl, subprocess, os, argparse

class Downloader:

    def __init__(self, quality = 43):
        initial_settings = {'outtmpl': '%(id)s.%(ext)s', 'format': str(quality)}

        self.ydl = youtube_dl.YoutubeDL(initial_settings)
        self.ydl.add_default_info_extractors()

    def get_video(self, url):
        info = self.ydl.extract_info(url, download=True)
        return self.ydl.prepare_filename(info)

    def remove_video(self, file):
        os.remove(file)


class Clipper:

    def __init__(self, filename, start, lenght):

        output = filename.split('.')[0] + '_clip.' + filename.split('.')[1]
        params = ['ffmpeg', '-i', filename, '-acodec', 'copy', '-vcodec', 'copy', '-y']

        if start:
            params.extend(['-ss', start])
        if lenght:
            params.extend(['-t', lenght])

        params.append(output)

        p = subprocess.Popen(params)
        p.communicate()


class WebmYT:

    def __init__(self, video, start, lenght, quality=1):
        sq = 43
        if quality == 2:
            sq = 45
        dwn_handler = Downloader(sq)
        filename = dwn_handler.get_video(video)
        Clipper(filename, start, lenght)

        dwn_handler.remove_video(filename)


def argvparser():
    parser = argparse.ArgumentParser(prog="yt_webm")
    parser.add_argument("video", help="Url of Youtube video to be downloaded.")
    parser.add_argument("-s", "--start", help="Set start point for the clip.", metavar="hh:mm:ss")
    parser.add_argument("-l", "--lenght", help="Set lenght of the clip.", metavar="hh:mm:ss")
    parser.add_argument("-q", "--quality", type=int, help="Quality of webm video.", choices=[1, 2])
    args = parser.parse_args()

    WebmYT(args.video, args.start, args.lenght, quality=args.quality)

argvparser()