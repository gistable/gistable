#! /usr/bin/python
# -*- coding: utf-8 -*-

# @author weishu @2015/12/7

import subprocess
import os
import re
import json

from AppKit import NSWorkspace, NSBundle
from pypinyin import lazy_pinyin

# copy from Alfred 2 preferences, if you have applications installed at other place, add it here.
APP_DIRECTORYS = [
    u'/Applications',
    u'/Applications/Xcode.app/Contents/Applications',
    u'/Developer/Applications',
    u'/Library/PreferencePannes',
    u'/opt/homebrew-cask/Caskroom',
    u'/System/Library/PreferencePannes',
    u'/usr/local/Cellar',
    u'~/Library/Caches/Metadata',
    u'~/Library/Mobile Documents',
    u'~/Library/PreferencePannes'
]

def _is_application(workspace, abspath):
    ''' is a `abspath` stand for a mac app'''
    return workspace.isFilePackageAtPath_(abspath)

def _get_app_pinyin_name(app_name):
    return reduce(lambda x, y: x + y, lazy_pinyin(app_name, errors='ignore'))

def _add_meta_data(app_pinyin_name, app_path):
    ''' add meta data(comments) to the app, which can help Alfred or SpotLight find it'''
    print "processing %s" % app_path
    try:
        subprocess.check_call('xattr -w com.apple.metadata:kMDItemFinderComment %s "%s"' % (app_pinyin_name, app_path), shell=True)
    except:
        print "process %s failed, ignore." % app_path
        
def _get_localized_name(abs_path):
    '''get the localized name of given app'''
    bundle = NSBundle.new()
    bundle.initWithPath_(abs_path)
    localizations = bundle.localizations()
    chinese = ('zh_CN', 'zh_Hans', 'zh-Hans', 'zh-CN')

    b = any(map(lambda x: x in localizations, chinese))
    if not b: return 

    for ch in chinese:
        path = bundle.pathForResource_ofType_inDirectory_forLanguage_('InfoPlist', 'strings', None, ch)
        if not path: continue
        # the path must surround with "", there may be space characters
        json_str = subprocess.check_output(u'plutil -convert json -o - "%s"' % path, shell=True)
        # print json_str
        json_res = json.loads(json_str, encoding='utf8')
        name = json_res.get('CFBundleName')
        if name: return name

def main():
    pattern = re.compile(r'^[\w\s.]+$')

    workspace = NSWorkspace.sharedWorkspace()

    for app_dir in APP_DIRECTORYS:
        if not os.path.exists(app_dir): continue

        for root, dirs, files in os.walk(app_dir, topdown=True):
            remove_list = []
            for directory in dirs:
                full_path = os.path.join(root, directory)
                # print full_path
                if not _is_application(workspace, full_path): continue

                remove_list.append(directory)
                try:
                    localized_name =  _get_localized_name(full_path)
                except:
                    print "get localized name for %s failed. ignore" % full_path
                    # continue
                
                # print "localized_name:", localized_name if localized_name else None
                app_name = localized_name if localized_name else directory.rsplit(r'.')[0]

                if pattern.match(app_name):
                    # print "app_name: %s not match" % app_name
                    continue
                try:
                    _add_meta_data(_get_app_pinyin_name(app_name), full_path)
                except:
                    # may be empty, just ignore
                    print "add meta for %s failed" % full_path

            # if this directory is already a Application
            # do not traverse this; some app may be very large 
            # and there won't be any other app inside it
            dirs[:] = [d for d in dirs if d not in remove_list]

if __name__ == '__main__':
    main()