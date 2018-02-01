#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import json
import getopt
import urllib2
from urllib import urlencode
from base64 import b64encode
from subprocess import Popen, PIPE, call
from datetime import datetime

APP_NAME = ""
CONFIG_NAME = "Release"
IPA_NAME = ""
HTTP_URL = ""
SFTP_SERVER = ""
SFTP_PATH = ""
NOTIF_EMAIL = "app@iweekly.mailgun.org"
EMAIL_DOMAIN = "iweekly.mailgun.org"
MAILGUN_KEY = "fill-your-mailgun-key-here"

def clean():
    call_shell(["xcodebuild", "clean"])
    call_shell(["rm", "-rf", "build"])
    print "All build files cleared."

def xcodebuild():
    print "Start building target %s ..." % APP_NAME
    cmd = ["xcodebuild", "-target", APP_NAME, "-configuration", CONFIG_NAME, "CONFIGURATION_BUILD_DIR=build",  "clean", "build"]
    call(cmd)

def package():
    print "Start packaging ..."
    call_shell(["rm", "-rf", "Payload"])
    os.mkdir("Payload")
    call_shell(["mv", "%s.app" % APP_NAME, "Payload"])
    call_shell(["zip", "-r", IPA_NAME, "Payload"])
    call_shell(["mv", IPA_NAME, "pkg"])

def prepare():
    print "Start preparing files for deploy ..."
    appName = "%s.app" % (APP_NAME)
    call_shell(["rm", "-rf", "pkg"])
    os.mkdir("pkg")

    call_shell(["cp", "%s/Info.plist" % appName, "Info.plist"])
    pl = plist_to_dictionary("Info.plist")

    global IPA_NAME
    IPA_NAME = "%s_%s_%s.ipa" % (APP_NAME, pl["CFBundleShortVersionString"], pl["CFBundleVersion"])

    icons = icons_file(pl)
    if icons[0]:
        call_shell(["cp", "%s/%s" % (appName, icons[0]), "pkg/%s" % icons[0]])
    if icons[1]:
        call_shell(["cp", "%s/%s" % (appName, icons[1]), "pkg/%s" % icons[1]])

    content = manifest(pl)
    f = open("pkg/%s.plist" % IPA_NAME, "w")
    f.write(content.encode('utf8'))
    f.close()

    content = index_html(pl)
    f = open("pkg/index.html", "w")
    f.write(content.encode('utf8'))
    f.close()

def sftp():
    print ""
    print "Start uploading files to %s ..." % SFTP_SERVER
    (width, height) = terminal_size()
    print "-" * width
    cmd = ["scp", "-r", "pkg/.", "%s:%s" % (SFTP_SERVER, SFTP_PATH)]
    call(cmd)
    print "-" * width
    print "Finished uploading files."
    print "Download app at %s" % HTTP_URL

def send_notification():
    print "Start sending notification emails ..."

    f = open("pkg/index.html", "r")
    content = f.read().decode('utf8')
    f.close()

    pl = plist_to_dictionary("Info.plist")
    appFullName = "%s %s (%s)" % (pl["CFBundleName"], pl["CFBundleShortVersionString"], pl["CFBundleVersion"])

    ret = send_mailgun(appFullName, content)
    ret = json.loads(ret)
    print ret["message"]

def manifest(pl):
    template = '''
<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>items</key>
      <array>
        <dict>
          <key>assets</key>
          <array>
            <dict>
              <key>kind</key>
              <string>software-package</string>
              <key>url</key>
              <string>%s</string>
            </dict>
            <dict>
              <key>kind</key>
              <string>full-size-image</string>
              <key>needs-shine</key>
              <false/>
              <key>url</key>
              <string>%s</string>
            </dict>
            <dict>
              <key>kind</key>
              <string>display-image</string>
              <key>needs-shine</key>
              <false/>
              <key>url</key>
              <string>%s</string>
            </dict>
          </array>
          <key>metadata</key>
          <dict>
            <key>bundle-identifier</key>
            <string>%s</string>
            <key>bundle-version</key>
            <string>%s</string>
            <key>kind</key>
            <string>software</string>
            <key>title</key>
            <string>%s</string>
          </dict>
        </dict>
      </array>
    </dict>
</plist>
    '''
    appUrl = HTTP_URL + "/" + IPA_NAME
    icons = icons_file(pl)
    icon2xUrl = HTTP_URL + "/" + icons[1]
    iconUrl = HTTP_URL + "/" + icons[0]

    return template % (appUrl, icon2xUrl, icon2xUrl, pl["CFBundleIdentifier"], pl["CFBundleVersion"], pl["CFBundleName"])

def index_html(pl):
    template = u'''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
<title>%s - Beta Release</title>
<style type="text/css">
body {background:#fff;margin:0;padding:0;font-family:arial,helvetica,sans-serif;text-align:center;padding:10px;color:#333;font-size:16px;}
#container {width:300px;margin:0 auto;}
h1 {margin:0;padding:0;font-size:14px;}
p {font-size:13px;}

.link {background:#ecf5ff;border-top:1px solid #fff;border:1px solid #dfebf8;margin-top:.5em;padding:.3em;}
.link a {text-decoration:none;font-size:15px;display:block;color:#069;}
.install_button {line-height:44px;margin:.5em auto;}
.install_button a {font-weight:bold;font-size:24px}
.last_updated {font-size: x-small;text-align: center;font-style: italic;}
.icon {border-radius:10px;box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);}
</style>
</head>
<body>

<div id="container">

<p><img class="icon" src='%s' height='57' width='57' /></p>

<h1>%s</h1>

<div class="link install_button"><a href="itms-services://?action=download-manifest&url=%s/%s.plist">INSTALL</a></div>
<p class="last_updated">此按钮仅在 iOS 设备上有效。</p>

<p><strong>更新内容</strong><br />
%s</p>

<p>Build on %s, by App Master</p>
</body>
</html>
    '''
    reason = get_editor_input()

    icons = icons_file(pl)
    icon2xUrl = "%s/%s" % (HTTP_URL, icons[1])

    timeStr = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    appFullName = "%s %s (%s)" % (pl["CFBundleName"], pl["CFBundleShortVersionString"], pl["CFBundleVersion"])
    return template % (appFullName, icon2xUrl, appFullName, HTTP_URL, IPA_NAME, reason, timeStr)

def get_editor_input():
    cmd = os.environ['EDITOR']
    if not cmd:
        cmd = "/usr/bin/vim"

    tmpFile = "/tmp/%s.input" % IPA_NAME
    f = open(tmpFile, "w")
    f.write("# What's NEW in this build?\n\n\n")
    f.close()
    call([cmd, tmpFile])
    f = open(tmpFile, "r")
    contents = f.read().decode('utf8').split("\n")
    f.close()

    result = ""
    for line in contents:
        line = line.strip()
        if line.find("#") == 0 or len(line) == 0:
            continue
        result += line + "<br/>"

    if len(result) == 0:
        result = "-"

    return result

def icons_file(pl):
    if "CFBundleIconFiles" in pl:
        return pl["CFBundleIconFiles"]
    elif "CFBundleIcons" in pl:
        return pl["CFBundleIcons"]["CFBundlePrimaryIcon"]["CFBundleIconFiles"]
    else:
        return ["",""]

def plist_to_dictionary(filename):
    "Pipe the binary plist through plutil and parse the JSON output"
    with open(filename, "rb") as f:
        content = f.read()
    args = ["plutil", "-convert", "json", "-o", "-", "--", "-"]
    p = Popen(args, stdin=PIPE, stdout=PIPE)
    p.stdin.write(content)
    out, err = p.communicate()
    return json.loads(out)

def call_shell(cmd):
    try:
        p = Popen(cmd, stdin=None, stdout=PIPE)
        out, err = p.communicate()
        retcode = p.returncode
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e

def terminal_size():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])

def send_mailgun(appName, message):
    api_url = "https://api.mailgun.net/v2/%s/messages" % EMAIL_DOMAIN;
    data={"from": "App Master <postmaster@%s>" % EMAIL_DOMAIN,
          "to": NOTIF_EMAIL,
          "subject": "%s is ready!" % appName,
          "text": "%s is ready!" % appName,
          "html": message.encode('utf-8')}

    request = urllib2.Request(api_url)

    print "Sending notification to:" + NOTIF_EMAIL

    request.add_header('Authorization', 'Basic ' + b64encode("api:%s" % MAILGUN_KEY))
    request.add_data(urlencode(data))

    try:
        r = urllib2.urlopen(request)
        return r.read()
    except OSError, e:
        print e


############################################################
# main
############################################################

def usage():
    print "This tool is used to make it easy to build and distribute enterprise iOS app."
    print "It also send out notification via eMails (via mailgun)"
    print ""
    print "# Usage: build.py [-h] -t target_name -s sftp_server -p sftp_path -u http_url [command]"
    print "# command = clean|upload|build|notif"

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ht:s:p:u:n:m:d:c:", ["help", "target=", "server=", "path=", "http_url=", "notif_email=", "mailgun_key=", "email_domain=", "configuration="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("-c", "--configuration"):
            global CONFIG_NAME
            CONFIG_NAME = arg
        if opt in ("-t", "--target"):
            global APP_NAME
            APP_NAME = arg
        if opt in ("-s", "--server"):
            global SFTP_SERVER
            SFTP_SERVER = arg
        if opt in ("-p", "--path"):
            global SFTP_PATH
            SFTP_PATH = arg
        if opt in ("-u", "--http_url"):
            global HTTP_URL
            HTTP_URL = arg
        if opt in ("-d", "--email_domain"):
            global EMAIL_DOMAIN
            EMAIL_DOMAIN = arg
        if opt in ("-n", "--notif_email"):
            global NOTIF_EMAIL
            NOTIF_EMAIL = arg
        if opt in ("-m", "--mailgun_key"):
            global MAILGUN_KEY
            MAILGUN_KEY = arg

    if argv and argv[-1] == "clean":
        clean()
        sys.exit(0)

    if argv and argv[-1] == "notif":
        os.chdir("build")
        send_notification()
        sys.exit(0)

    if not APP_NAME or not SFTP_SERVER or not SFTP_PATH or not HTTP_URL:
        usage()
        sys.exit(2)

    if argv and argv[-1] == "build":
        clean()
        xcodebuild()
        os.chdir("build")
        prepare()
        package()
        sys.exit(0)

    if argv and argv[-1] == "upload":
        os.chdir("build")
        sftp()
        sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])