# -*- coding: utf8 -*-

import os, simplejson, re

class OrganizerException(Exception):
    
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return  self.message


class Organizer(object):

    def __init__(self, configFile):
        self.__preserveConfig(configFile)

    """
    gets config parameter and returns config dictionary.
    """
    def __preserveConfig(self, configFile):
        if os.path.exists(configFile) == False:
            raise OrganizerException(\
                                        u"check the existance of config file: %s" % configFile\
                                    )

        file_content = open(configFile).read()

        try:
            self.config  = simplejson.loads(file_content)
        except ValueError:
            raise OrganizerException(\
                                        u"config file is not valid. check it"\
                                    )
        if not self.config.has_key("dir_for_unknown_files"):
            raise OrganizerException(\
                                        u"[dir_for_unknown_files] key doesn't exists in your config file."\
                                    )

        if not self.config.has_key("rules"):
            raise OrganizerException(\
                                        u"there is no 'rules' variable in json config."\
                                    )

    """
    returns 'listed files' in the target directory.
    """
    def getFileList(self):
        files = os.listdir(self.config.get("target_dir"))
        return files
    
    """
    handler function for listed files.
    """
    def handleFiles(self):
        files     = self.getFileList()
        root_path = self.config.get("target_dir")
        for file in files:
            # get all files
            if os.path.isfile("%s/%s" % (self.config.get("target_dir"), file)):
                # play with files that has extension
                if self.hasExtension(file):
                   move_dir = self.findMoveDirectory(file)
                   os.rename("%s/%s" % (root_path, file),\
                             "%s/%s/%s" % (root_path, move_dir, file))
                   self.__printNotification("%s to %s" % (file, move_dir))

    """
    returns rules for file move actions
    """
    def getRules(self):
        return self.config.get("rules")

    """
    returns the extension of file.
    """
    def getExtension(self, fileName):
        search = re.search(".*\.(.*?)$", fileName)
        if not search == None:
            return search.group(1)
        else:
            return False

    """
    file has an extension or not?
    """
    def hasExtension(self, fileName):
        if self.getExtension(fileName) == False:
            return False

        return True

    """
    returns new 'move' directory for file
    """
    def findMoveDirectory(self, fileName):
        rules = self.getRules()
        match = 0
        for regex_rule, target_dir in rules.iteritems():
            if(re.search(regex_rule, fileName)):
                self.controlTargetDir(target_dir)
                match = 1
                return target_dir

        # no match, return 'unknown' directory
        if match == 0:
            unknown = self.config.get("dir_for_unknown_files")
            self.controlTargetDir(unknown)
            return unknown

    def __printNotification(self, notification):
        print " [+] %s" % notification

    """
    if file's new destination is not created yet, don't stop the music.
    """
    def controlTargetDir(self, subTargetDir):
        full_dir = "%s/%s" % (self.config.get("target_dir"), subTargetDir)

        if not os.path.isdir(full_dir):
            self.__printNotification("%s is not a directory. creating." % subTargetDir)
            os.mkdir(full_dir)


if __name__ == "__main__":
    # initial setup
    organizer = Organizer("config.json")
    organizer.handleFiles()
