import requests
from tqdm import tqdm
import os
import sys

def Logo():
	print ('''
 /$$   /$$ /$$       /$$      
| $$  | $$| $$      | $$      
| $$  | $$| $$$$$$$ | $$$$$$$ 
| $$$$$$$$| $$__  $$| $$__  $$
| $$__  $$| $$  \ $$| $$  \ $$
| $$  | $$| $$  | $$| $$  | $$
| $$  | $$| $$$$$$$/| $$  | $$
|__/  |__/|_______/ |__/  |__/ 1.0                          
''')                              
                              
def main():
	Sis()
	Logo()
	Conectar()
	Bruteforce()

def Sis():
	if sys.platform != "linux2":
		os.system("cls")
	else:
		os.system("clear")

def Conectar():
	print ("\n[+] Heaven Brute Hex")
	print ("\n[+] Skype - gilmarsilva98 | Twitter - gilmarsilva_")
	global host,n1,n2,read
	host = input("\nDigite a url: ")
	n1 = int(input("\nPonto inicial: "))
	n2 = int(input("\nPonto Final: "))
	read = input("\nDigite o que quer filtrar: ")

def Bruteforce():
	for hvn in tqdm(range(n1,n2)):
		hvn = hex(hvn).split('x')[1]
		r = requests.get(host+str(hvn))
		heaven = (r.content)
		if read in str(heaven):
			print (str(heaven))
			quit()

main()