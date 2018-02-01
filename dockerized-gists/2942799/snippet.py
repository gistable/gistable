import base64
import sys

def main():
	if len(sys.argv) < 3:
		sys.exit('Usage (2 arguments): %s "%s" %s' % (sys.argv[0],"malicious file","outfile"))
	else:
		f = open(sys.argv[1],"rb")
		con = f.read()
		f.close()

		start = '<?xml version="1.0"?><?xfa ?><xdp:xdp xmlns:xdp="http://ns.adobe.com/xdp/"><pdf xmlns="http://ns.adobe.com/xdp/pdf/"><document><chunk>'
		encoded = base64.b64encode(con)
		end = "</chunk></document></pdf></xdp:xdp>"

		f = open(sys.argv[2],"wb")
		f.write(start + encoded + end)
		f.close()

if __name__ == '__main__':
	main()