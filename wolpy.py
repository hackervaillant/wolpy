#!/usr/bin/env python3

import argparse
import ipaddress
import re
import socket
import sys


def sendMagicPacket(mac, ip, port):
    
    if ip.version == 6:
        socktype = socket.AF_INET6
    
    else:
        socktype = socket.AF_INET

    # Build payload
    magicpattern = 6 * 'ff' + 16 * mac.replace(':', '').replace('-', '')
    payload = bytearray.fromhex(magicpattern)

    # Open an UDP socket and allow broadcasts
    s = socket.socket(socktype, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send an close
    s.sendto(payload, (ip.compressed, port))
    s.close()
    

def macAddress(value):
    
    if re.match('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', value):
        return value
        
    else:
        raise argparse.ArgumentTypeError("Invalid MAC address.")
    
    
def udpPort(value):
    
    try:
        port = int(value)
        assert 0 <= port <= 65535
    
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError("Port must be 0-65535.")
    
    else:
        return port


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("mac", help="MAC Address", type=macAddress)
    parser.add_argument("-i", "--ip", help="IP Address", type=ipaddress.ip_address, default='255.255.255.255')
    parser.add_argument("-p", "--port", help="UDP Port", type=udpPort, default=9)

    try:
        args = parser.parse_args()
        sendMagicPacket(**vars(args))
        
    except SystemExit:
        return 2

    except Exception as err:
        print(err, file=sys.stderr)
        return 1

    else:
        return 0

    
if __name__ == '__main__':
    sys.exit(main())
