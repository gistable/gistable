    #!/usr/bin/env python
    # encoding: utf-8
    """emlx.py

    Class to parse email stored with Apple proprietary emlx format
    Created by Karl Dubost on 2013-03-30
    Inspired by Rui Carmo — https://the.taoofmac.com/space/blog/2008/03/03/2211
    MIT License"""


    import email
    import plistlib


    class Emlx(object):
        """An apple proprietary emlx message"""
        def __init__(self):
            super(Emlx, self).__init__()
            self.bytecount = 0
            self.msg_data = None
            self.msg_plist = None

        def parse(self, filename_path):
            """return the data structure for the current emlx file
            * an email object
            * the plist structure as a dict data structure
            """
            with open(filename_path, "rb") as f:
                # extract the bytecount
                self.bytecount = int(f.readline().strip())
                # extract the message itself.
                self.msg_data = email.message_from_bytes(f.read(self.bytecount))
                # parsing the rest of the message aka the plist structure
                self.msg_plist = plistlib.readPlistFromBytes(f.read())
            return self.msg_data, self.msg_plist

    if __name__ == '__main__':
        msg = Emlx()
        message, plist = msg.parse('your_message.emlx')
        # print(message)
        # Access to one of the email headers
        print(message['subject'])
        # Access to the plist data
        print(plist)