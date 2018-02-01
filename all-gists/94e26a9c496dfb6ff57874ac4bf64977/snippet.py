"""while True:
    print "What do you see?"
    ans = raw_input("> ")
    
    if (ans == ""):
        break
    
    else:
        if ans.endswith("."):
            print '"note:"' + '"' + ans + '"'
        else:
            print '"note:"' + '"' + ans + '"' + "."
            
print "I shall stop asking questions"
"""
nwrong = 0

while True:
    code = raw_input("Door Code: ")
    code = str(code)
    
    if code.isdigit() and (len(code) == 4):
        
        if code == "8888":
            break
        
        else:
            nwrong = nwrong + 1
            print "Wrong Guesses:", nwrong
    
    else:
        print "Invalid!"

print "Welcome to Mars!"