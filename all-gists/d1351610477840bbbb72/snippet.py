# weechat script to display image in terminal
# (tested in termite, which is based on vte-ng)
# requirements:
#   * weechat (of course)
#   * w3m (for w3mimgdisplay)
#   * imlib2-webp (optional, for webp support)
#
# save this script as ~/.weechat/python/test.py and load using
#   /python load test.py
# in weechat.
# use at your own risk!

import weechat
import glob
import subprocess
import itertools
import os
import re
import tempfile


W3MIMGDISPLAY = "/usr/lib/w3m/w3mimgdisplay"
IMGURL = re.compile(r'https?://.*\.(jpg|jpeg|png|webp)')
images = {}
count = itertools.count()


class TempImage:
    def __init__(self, url):
        self.url = url
        self.fname = ''
        self.hook = None
        self.downloaded = False
        self.id = count.next()
        images[self.id] = self

    def start_download(self):
        fd, self.fname = tempfile.mkstemp(dir=TEMPDIR)
        os.close(fd)
        self.hook = weechat.hook_process_hashtable(
            "url:" + self.url,
            {'file_out': self.fname},
            30 * 1000, "download_finish_cb", str(self.id))

    def download_finish_cb(self):
        self.downloaded = True

    @staticmethod
    def display_image(path):
        if not os.path.exists(path):
            return
        p = subprocess.Popen(W3MIMGDISPLAY,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, _ = p.communicate("5;%s" % path)
        width, height = map(int, output.split())
        p = subprocess.Popen(W3MIMGDISPLAY,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, _ = p.communicate("0;1;0;0;%d;%d;;;;;%s\n4;\n3;" %
                                  (width, height, path))

    def display(self):
        self.display_image(self.fname)


def download_finish_cb(data, command, rc, out, err):
    if int(rc) == 0:
        images[int(data)].download_finish_cb()
    elif int(rc) > 0:
        weechat.prnt("", "Failed downloading image %s (rc=%s)" %
                     (images[int(data)].url, rc))
    return weechat.WEECHAT_RC_OK


def msg_cb(data, modifier, modifier_data, string):
    parsed = weechat.info_get_hashtable("irc_message_parse",
                                        {'message': string})
    message = parsed['text']
    result = IMGURL.search(message)
    if not result:
        return string
    url = result.group()
    image = TempImage(url)
    image.start_download()
    return string + " [ID=%d]" % image.id


def showimage_cb(data, source_buffer, args):
    args = args.split()
    if len(args) < 1:
        weechat.prnt(source_buffer, "Please specify image ID")
        return weechat.WEECHAT_RC_OK

    try:
        image = images[int(args[0])]
        if image.downloaded:
            image.display()
        else:
            weechat.prnt(source_buffer, "Image %s is still being downloaded" %
                         args[0])
    except (ValueError, KeyError):
        weechat.prnt(source_buffer, "No such image")

    return weechat.WEECHAT_RC_OK


def unload(*args):
    map(os.unlink, glob.glob(os.path.join(TEMPDIR, '*')))
    os.rmdir(TEMPDIR)
    return weechat.WEECHAT_RC_OK


if __name__ == '__main__':
    if not os.path.exists(W3MIMGDISPLAY):
        weechat.prnt("", "w3m image display utility not found")
    else:
        TEMPDIR = tempfile.mkdtemp(prefix="weechatpreview")
        weechat.register("weechatpreview", "hexchain", "1.0", "GPL3",
                         "Preview image links",
                         "unload", "")

        weechat.hook_modifier("irc_in2_privmsg", "msg_cb", "")
        weechat.hook_modifier("irc_out1_privmsg", "msg_cb", "")
        weechat.hook_command("showimage",
                             "Display specified image", "", "", "",
                             "showimage_cb", "")
