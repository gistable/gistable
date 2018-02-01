#!/usr/bin/env python

import sys, getopt, random


def main(inputpass):

  try:
      passopts, passargs = getopt.getopt(inputpass, "hl:n:d:s:f:", ["help", "length=", "digits=", "special=", "file="])

  except getopt.GetoptError:
      usage()
      sys.exit(2)


  for npassopts, npassargs in passopts:
      if npassopts in ("-h", "--help"):
          help()
          sys.exit(2)
      elif npassopts in ("-l", "--length"):
              lenpasswd = check_digi(npassargs)
      elif npassopts in ("-d", "--digits"):
              pwdigits = check_digi(npassargs)
      elif npassopts in ("-s", "--special"):
             special =  check_digi(npassargs)
      elif npassopts in ("-f", "--file"):
             file = file_check(npassargs)
             #print "Previous passwd from file: " + file
             
  try:
      rpasswd = switch(file)
      #if len(rpasswd) >= lenpasswd:
      print rpasswd   
  except UnboundLocalError:
      usage()
      sys.exit(2)


def help():
   print "This is the help menu."



def switch(selpasswd):
    selpasswdlen = len(selpasswd) - 1
    mypasswd = list(selpasswd)

    mychar = ['a', 'A', "@", 'b', 'B', '8', 'e', 'E', '3', 'l', 'L', '!', 'i', 'I', '1', 'o', 'O', '0', 's', 'S', '5', '$', 't', 'T', '+', '9', 'p', 'P', 'h', 'H', '4']

    alist = len(mychar) - 1


    for i in range(selpasswdlen):
      for j in range(alist):
        if mypasswd[i] in mychar:
          mypasswd[i] = random.choice(mychar)

    #print "Modified passwd: " + ''.join(mypasswd)
    return ''.join(mypasswd)
 

def check_digi(num):
    if num.isdigit():
       return num
    else:
       print num + " is an invalid option..exiting" 
       sys.exit(2)


def file_check(passfile):
    try:
        f = open(passfile, 'r')
        pwlists = f.readlines()
        lspasswd = len(pwlists) -1
        lnum = random.randint(0, lspasswd)
        return pwlists[lnum].strip()
    except IOError:
        print "File does not exist..exiting"
        sys.exit(2)



def usage():
    print "Usage: genpass.py [-l] <num> [-d] <num> [-s] <num> -f <filename>"



if __name__ == "__main__":
    main(sys.argv[1:])
