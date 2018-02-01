import datetime
import os
import sys
import pefile
from scapy.all import *
import scapy_http.http
import tempfile

TIME_THRESHOLD = datetime.timedelta(days=3)

def analyse_http_response(packet):
	""" Check if response data is a PE file without any other check """
	print("[+] Got a file")
	f = tempfile.NamedTemporaryFile(delete=False)
	try:
		f.write(packet[4].load)
		f.close()
	except:
		os.remove(f.name)

	try:
		pe = pefile.PE(f.name)
		print("[+] Detected a PE file in HTTP response")
		detect_freshly_compiled_pe(pe, f.name)
	except pefile.PEFormatError:
		os.remove(f.name)
		pass
	except Exception as e:
		print(e)

def detect_freshly_compiled_pe(pe, file_path):
	""" Parse PE file header to read compilation timestamp """
	ts = pe.FILE_HEADER.TimeDateStamp
	compiled_at = datetime.datetime.fromtimestamp(ts)
	if (datetime.datetime.now() - compiled_at) <= TIME_THRESHOLD:
		print("[+] Possible malware detected! %s (compiled at %s)" % (os.path.basename(file_path), compiled_at))
		print("[+] Sample saved at %s" % (file_path))
	else:
		print("[+] Compilation date seems old (%s)" % compiled_at)
		os.remove(file_path)

def main(argv):
	if len(argv) == 2:
		print("[+] Listening on %s..." % argv[1])
		sniff(iface=argv[1],
			prn=analyse_http_response,
			lfilter= lambda x: x.haslayer(scapy_http.http.HTTPResponse))
	else:
		print("Usage: %s <listening interface>" % argv[0])
		sys.exit(1)

if __name__ == '__main__':
	try:
		main(sys.argv)
	except Exception:
		import traceback
		traceback.print_exc()
