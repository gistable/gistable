import random

# Pattern Key || Number to enter
# 	0 		=====> 	1
# 	1 		=====> 	2
# 	2 		=====> 	3
# 	3 		=====> 	4

def match_password(pattern, entered_pas, db_password):
	session_pass = []
	for i in range(len(pattern)):
		#print db_password[pattern[i]]
		session_pass.append(db_password[pattern[i]]) # make session password based on the generated pattern
	
	print "Session pass %s" % ''.join(map(str,session_pass)) # Convert the session pass [] to a string
	print "Entered password %s " % entered_pas

	if ''.join(map(str,session_pass)) == entered_pas:
		return True
	else:
		return False


if __name__=='__main__':
	db_password = [1,2,3,4] # Should be secretly stored in DB

	pattern = []
	for i in range(0,4):
		pattern.append(random.randint(0, 3)) # only show numbers in pattern upto 3 (fourth element)

	print "Pattern "
	print pattern
	entered_pas = raw_input("Enter you PIN...")

	if match_password(pattern, entered_pas, db_password):
		print "Successfully authenticated !"
	else:
		print "Access Denied !"