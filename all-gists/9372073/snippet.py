import sys
import win32com.client
openedDoc = win32com.client.Dispatch("Excel.Application")
filename= sys.argv[1]

password_file = open ( 'wordlist.lst', 'r' )
passwords = password_file.readlines()
password_file.close()

passwords = [item.rstrip('\n') for item in passwords]

results = open('results.txt', 'w')

for password in passwords:
	print(password)
	try:
		wb = openedDoc.Workbooks.Open(filename, False, True, None, password)
		print("Success! Password is: "+password)
		results.write(password)
		results.close()
	except:
		print("Incorrect password")
		pass
