#!/usr/bin/python
'''Get LAPS password for AD Computers'''
# #################################################################
# This script will allow an admin user with
# the proper domain crednetials to get a LAPS
# password form Active Directory.
# ##################################################################
# Original script by barteardon
# https://github.com/bartreardon/macscripts/blob/master/lapssearch
# Updated script using pyObjC:
# Joshua D. Miller - josh@psu.edu
# The Pennsylvania State University - September 18, 2017
# #################################################################
from getpass import getpass
from os import system
from OpenDirectory import (ODSession, ODNode,
                           kODRecordTypeComputers)
from SystemConfiguration import (SCDynamicStoreCreate,
                                 SCDynamicStoreCopyValue)


class color:
    # From Stack Overflow
    # https://stackoverflow.com/questions/
    # 8924173/how-do-i-print-bold-text-in-python
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def macOSLAPS_Utility(choice, ad_user_name, ad_password, computer_name):
        '''Function to connect and pull information from Active Directory
        some code borrowed from AD PassMon - Thanks @macmuleblog'''
        # Active Directory Connection and Extraction of Data
        try:
            # Create Net Config
            net_config = SCDynamicStoreCreate(None, "net", None, None)
            # Get Active Directory Info
            ad_info = dict(
                SCDynamicStoreCopyValue(
                    net_config, 'com.apple.opendirectoryd.ActiveDirectory'))
            # Create Active Directory Path
            adpath = '{0:}/{1:}'.format(ad_info['NodeName'],
                                        ad_info['DomainNameDns'])
            # Use Open Directory To Connect to Active Directory
            node, error = ODNode.nodeWithSession_name_error_(
                ODSession.defaultSession(), adpath, None)
            node.setCredentialsWithRecordType_recordName_password_error_(
                None, ad_user_name, ad_password, None)
            # Grab the Computer Record
            computer_record, error = node.\
                recordWithRecordType_name_attributes_error_(
                    kODRecordTypeComputers,
                    "{0:}$".format(computer_name), None, None)
            # Convert to Readable Values
            values, error = computer_record.\
                recordDetailsForAttributes_error_(None, None)
            # Get LAPS Password for machine
            if choice == "1":
                print "Password: {0:}{1:}{2:}".format(
                    color.BOLD,
                    values['dsAttrTypeNative:ms-Mcs-AdmPwd'][0],
                    color.END)
                raw_input("\n\nPress any key to continue....")
            elif choice == "2":
                computer_record.setValue_forAttribute_error_(
                    '126227988000000000',
                    'dsAttrTypeNative:ms-Mcs-AdmPwdExpirationTime',
                    None)
                raw_input("\n\nForce Expire time Set. Keep in mind that"
                          " macOSLAPS will need to run on the system before"
                          " the password is changed."
                          " Press any key to continue...")
        except StandardError as error:
            print error


def main():
    '''Main function of macOSLAPS Password retrieval utility'''
    print "Welcome to the macOSLAPS Utility"
    ad_user_name = raw_input("Please enter your username:")
    ad_password = getpass("Please enter your password:")
    choice = "0"
    while choice != "3":
        system('clear')
        print "macOSLAPS Utility"
        print "-----------------"
        print "1. Get LAPS Password"
        print "2. Reset LAPS Password"
        print "3. Exit"
        choice = raw_input("\n >>  ")
        if choice != "1" and choice != "2" and choice != "3":
            raw_input("\n\nPlease enter a valid choice"
                      " (Example \"1\", \"2\", \"3\")")
            continue
        if choice == "3":
            print "Thank you for using macOSLAPS Utility!"
            continue
        computer_name = raw_input("Computer Name: ")
        macOSLAPS_Utility(choice, ad_user_name, ad_password, computer_name)
        continue

    exit(0)


if __name__ == "__main__":
    main()
