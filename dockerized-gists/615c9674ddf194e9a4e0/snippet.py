import os

def readCfg(location):
	# Make sure file exists...
	if not os.path.exists(location):
		return False
	with open(location) as f:
		cfg= {}
		for line in f:
			line = line.strip()
			# Ignore invalid lines
			if line and not line.startswith("#") and '=' in line:
				cfg[line.split('=', 1)[0]] = line.split('=', 1)[1]
		return cfg

if __name__ == "__main__":
	cfg = readCfg('/home/user/.bitcoin/bitcoin.conf')
	print(" %s ( :3 )" % cfg['rpcpassword'])