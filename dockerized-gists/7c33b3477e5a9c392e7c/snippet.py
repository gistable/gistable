# -*- coding: utf-8 -*-
#/usr/bin/python3
"""
flash
 April 21, 28, may 5, may 12, may 19

arrow
  april 22, 29, may 6, may 13

person of interest
  april 28, may 5

blacklist
  april 23, april 30
""" 

def main():
    from gi.repository import Notify   
    year=2015
    
    from datetime import datetime
    
    today = datetime.today()
    a = (today.month,today.day)
    ayear = today.year
    n = Notify.init("reminder")
    found=False
    
    list_ep=[(4,21),(4,28), (4,22), (4,23), (5,5), (5,12), (5,19), (4,29), (5,6), (5,13),(2,23), (4,30)]
    
    if a in list_ep and year==ayear:
        serial = find_name(a)
        if serial:
            n = Notify.Notification.new("A new episode today!", "of "+ serial)
    else:
        n = Notify.Notification.new("No new episode today")
    n.show()
"""             for ep in list_ep:
                if a[0] in ep and :
                    print(ep)
                    serial = find_name(ep)
                    n = Notify.Notification.new("An all new %s coming on %d/%d"%(serial,a[1], a[0]))
                    n.show()
                else:
                    n = Notify.Notification.new("No new episode any time soon :(")
"""

def find_name(a):
    flash=[(4,21), (4,28), (5,5), (5,12), (5,19)]
    arrow=[(4,22),(4,28),(4,29), (5,6), (5,13)]
    blacklist=[(4,23), (4,30)]
    person_of_interest=[(4,17),(4,28), (5,5)]
    serial=""
    
    if a in flash:
        if serial: serial+=" and flash" 
        else: serial="flash"
    if a in arrow:
        if serial: serial+=" and arrow" 
        else: serial="arrow"
    if a in blacklist:
        if serial: serial+=" and blacklist" 
        else: serial="blacklist"
    if a in person_of_interest:
        if serial: serial+=" and Person of Interest" 
        else: serial="Person of Interest"
    
    if serial !="":
        return serial

if __name__=='__main__':
    main()