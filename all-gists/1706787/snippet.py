import socket, ssl, json, struct
import binascii

# device token returned when the iPhone application
# registers to receive alerts
deviceToken = '39cac56f 986a0e66 3c4fd4f4 68df5598 024d2ca3 8b9f307c 741c180e 9fc30c62'

thePayLoad = {
     'aps': {
          'alert':'Oh no! Server\'s Down!',
          'sound':'k1DiveAlarm.caf',
          'badge':42,
          },
     'test_data': { 'foo': 'bar' },
     }

# Certificate issued by apple and converted to .pem format with openSSL
theCertfile = 'cert_ios_production.pem'
# 
theHost = ( 'gateway.push.apple.com', 2195 )

# 
data = json.dumps( thePayLoad )

# Clear out spaces in the device token and convert to hex
deviceToken = deviceToken.replace(' ','')
# byteToken = bytes.fromhex( deviceToken )
byteToken = binascii.unhexlify(deviceToken)

print("HELLOS")
print(byteToken)

theFormat = '!BH32sH%ds' % len(data)
theNotification = struct.pack( theFormat, 0, 32, byteToken, len(data), data )

#Just writing to a file for hex inspection
f = open('the_notification', 'w')
f.write(theNotification)
f.close()

# Create our connection using the certfile saved locally
ssl_sock = ssl.wrap_socket( socket.socket( socket.AF_INET, socket.SOCK_STREAM ), certfile = theCertfile )
ssl_sock.connect( theHost )

# Write out our data
ssl_sock.write( theNotification )

# Close the connection -- apple would prefer that we keep
# a connection open and push data as needed.
ssl_sock.close()