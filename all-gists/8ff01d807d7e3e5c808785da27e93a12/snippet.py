

                                         # A simple password program!
counter =0
AD = "Access Denied"        #sets a counter to 0 and inputs Both outputs as variables
AG = "Access Granted!"
while True:                 #creates an infinet loop
    password = raw_input("Enter the password")          #(MAIN FEATURE) asks for the password
    if password == "asdf":
        print ("\n\t\t\t\t\t %s" % (AG))        #If password correct then says 'access granted' (Then terminates)
        break
    else:
        print("\n\t\t\t\t\t %s Try Again" % (AD))
        counter+= 1                 #tells you if the password is wrong by saying 'access denied' (gives you 5 chances)
    if counter == 5:
        print("\n\t\t\t\t\t\t   %s \n\t\t\t\t\t You have been locked out!" % (AD))
                    #says 'You have been locked out!' and terminates program if all five chances are used up
        break



