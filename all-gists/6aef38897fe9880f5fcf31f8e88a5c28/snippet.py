mport NetworkManager
networks = []
SSID = None
for dev in NetworkManager.NetworkManager.GetDevices():
	if dev.Interface != 'wlan0':
		continue
	
	# Enumerate available networks
	for ap in dev.SpecificDevice().GetAccessPoints():
		# Skip non-AP SSIDs
		if ap.Mode != 2:
			continue
		#print (dir(ap))
		print (ap.Ssid, ap.WpaFlags, ap.Strength)
