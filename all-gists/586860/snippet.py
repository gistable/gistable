import os
import subprocess


# Open file corresponding to the TUN device.
tun = open('/dev/tun0', 'r+b')

# Bring it up and assign addresses.
subprocess.check_call('ifconfig tun0 192.168.7.1 192.168.7.2 up', shell=True)

while True:
    # Read an IP packet been sent to this TUN device.
    packet = list(os.read(tun.fileno(), 2048))

    # Modify it to an ICMP Echo Reply packet.
    #
    # Note that I have not checked content of the packet, but treat all packets
    # been sent to our TUN device as an ICMP Echo Request.

    # Swap source and destination address.
    packet[12:16], packet[16:20] = packet[16:20], packet[12:16]
    # Change ICMP type code to Echo Reply (0).
    packet[20] = chr(0)
    # Clear original ICMP Checksum field.
    packet[22:24] = chr(0), chr(0)
    # Calculate new checksum.
    checksum = 0
    # for every 16-bit of the ICMP payload:
    for i in range(20, len(packet), 2):
        half_word = (ord(packet[i]) << 8) + ord(packet[i+1])
        checksum += half_word
    # Get one's complement of the checksum.
    checksum = ~(checksum + 4) & 0xffff
    # Put the new checksum back into the packet.
    packet[22] = chr(checksum >> 8)
    packet[23] = chr(checksum & ((1 << 8) - 1))

    # Write the reply packet into TUN device.
    os.write(tun.fileno(), ''.join(packet))