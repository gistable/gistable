import websocket, thread, time, json, datetime, sys, os

def set_exit_handler(func):
    if os.name == "nt":
        try:
            import win32api
            win32api.SetConsoleCtrlHandler(func, True)
        except ImportError:
            version = ".".join(map(str, sys.version_info[:2]))
            raise Exception("pywin32 not installed for Python " + version)
    else:
        import signal
        signal.signal(signal.SIGTERM, func)

clear = lambda: os.system('cls')
number_of_transactions = 0
number_of_bitcoins = 0
large_transactions = []
apt = 0
output = ""

def write(text):
    f.write(text)

def on_message(ws, message):
	message = json.loads(message)
	amount = (float(message['x']['inputs'][0]['prev_out']['value'])/100000000)
	global number_of_transactions
	global number_of_bitcoins
	number_of_transactions += 1
	number_of_bitcoins += float(amount)

	if amount > apt:
		large_transactions.append(message['x'])

	printData()

def printData():
	clear()
	elapsed_time = time.time() - start_time
	elapsed_time_str = str(datetime.timedelta(seconds=elapsed_time))
	bps = (number_of_bitcoins / (elapsed_time))
	bpm = (number_of_bitcoins / (elapsed_time / 60))
	bph = (number_of_bitcoins / (elapsed_time / 3600))
	bpd = (number_of_bitcoins / (elapsed_time / 86400))
	global apt, output
	apt = float(number_of_bitcoins/number_of_transactions)
	output = ""
	output += ("Elapsed Time 	 : %s\n" % elapsed_time_str)
	output += ("# of Transactions: %d\n" % number_of_transactions)
	output += ("# of Bitcoins	 : %f\n" % float(number_of_bitcoins))
	output += ("Average per TXN  : %s\n" % apt)
	output += ("Bitcoins/second  : %s\n" % bps)
	output += ("Bitcoins/minute  : %s\n" % bpm)
	output += ("Bitcoins/hour    : %s\n" % bph)
	output += ("Bitcoins/day     : %s\n" % bpd)
	output += ("\n")

	for txn in large_transactions[-10::]:
		output += (txn['hash'] + " ")
		output += str(float(txn['inputs'][0]['prev_out']['value'])/float(100000000))
		output += ("\n")

	print output

def on_error(ws, error):
	print "ERROR: %s" % error
	f.close()
	sys.exit()

def on_close(ws):
	print "### closed ###"
	f.close()
	sys.exit()

def on_open(ws):
	ws.send("{\"op\":\"unconfirmed_sub\"}")

if __name__ == "__main__":
	def on_exit(sig, func=None):
		global f
		f = open('output_%s.txt' % output.split("\n")[0].split(" ")[-1::][0].replace(":", "_"), 'w+')
		f.write(output)
		f.close()

	set_exit_handler(on_exit)

	start_time = time.time()

	websocket.enableTrace(True)

	ws = websocket.WebSocketApp("ws://ws.blockchain.info:8335/inv",
	                          on_message = on_message,
	                          on_error = on_error,
	                          on_close = on_close)
	ws.on_open = on_open

	ws.run_forever()
