#!/usr/bin/env python

# Run this script on the agent.log file after you've run the situational_awareness/network/powerview/get_user module.
# userdata.log file is pipe delimited.

import sys
import os

class User:
    UserName = ""
    DN = ""
    Name = ""
    Email = ""
    Title = ""
    PwdLastSet = ""
    UAC = ""
    LastLogon = ""
    AdminCount = ""
    MemberOf = ""


if len(sys.argv) < 2:
    print "Usage: python parseagentlog.py /path/to/agent.log"
    exit()
else:
    logfile = sys.argv[1]
    if not os.path.isfile(logfile):
        print "Invalid path. Try again"
        exit()

def writelog(users):
    if users:
        with open("userdata.log", 'w') as output:
            output.write("USERNAME|NAME|DN|EMAIL|TITLE|PWDLASTSET|UAC|LASTLOGON|ADMINCOUNT\n")
            for u in users:
                if u.AdminCount:
                    admincount = "1"
                else:
                    admincount = "0"

                data = "{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}\n".format(
                    u.UserName,
                    u.Name,
                    u.DN,
                    u.Email,
                    u.Title,
                    u.PwdLastSet,
                    u.UAC,
                    u.LastLogon,
                    admincount
                )
                #print data
                output.write(data)
        print "{0} users written to userdata.log".format(users.__len__())
    else:
        print "No user data found."


with open(logfile, 'r') as log:
    lines = log.readlines()
    Users = list()
    user = ""

    for l in lines:
        if l.find('adspath') > -1:
            # Start of a new user
            if user:
                Users.append(user)

            user = User()

        vars = l.split(':')
        key = vars[0].strip()

        if key:
            if vars.__len__() > 1:
                val = vars[1]

                if val:
                    val = val.strip().rstrip('\n')

                    if key.find('useraccountcontrol') > -1:
                        user.UAC = val

                    if key.find('distinguishedname') > -1:
                        user.DN = val

                    if key.find('name') > -1:
                        user.Name = val

                    if key.find('mail') > -1:
                        user.Email = val

                    if key.find('title') > -1:
                        user.Title = val

                    if key.find('pwdlastset') > -1:
                        user.PwdLastSet = val.split(' ')[0]

                    if key.find('samaccountname') > -1:
                        user.UserName = val

                    if key.find('lastlogontimestamp') > -1:
                        user.LastLogon = val.split(' ')[0]

                    if key.find('admincount') > -1:
                        user.AdminCount = val

    writelog(Users)