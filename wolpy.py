#!/usr/bin/env python3

# wolpy sends wake-on-lan magic packets across IP and IPv6 networks

# Copyright (C) 2018  Hacker Vaillant
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import ipaddress
import re
import socket
import sys


def sendMagicPacket(mac, ip, port):
    """Builds and sends the magic packet."""
    
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

    # Send and close
    s.sendto(payload, (ip.compressed, port))
    s.close()
    

def macAddress(value):
    """argparse helper for MAC addresses."""
    
    if re.match('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', value):
        return value
        
    else:
        raise argparse.ArgumentTypeError("Invalid MAC address.")
    
    
def udpPort(value):
    """argparse helper for UDP ports."""
    
    try:
        port = int(value)
        assert 0 <= port <= 65535
    
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError("Port must be 0-65535.")
    
    else:
        return port


def main():
    
    DESCRIPTION = """
    wolpy sends wake-on-lan magic packets across IP and IPv6 networks.
    """
    
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("mac", help="MAC Address", type=macAddress)
    parser.add_argument("-i", "--ip", help="Broadcast IP address, defaults to 255.255.255.255", type=ipaddress.ip_address, default='255.255.255.255')
    parser.add_argument("-p", "--port", help="UDP Port, defaults to 9", type=udpPort, default=9)

    try:
        args = parser.parse_args()
        sendMagicPacket(**vars(args))
        
    except SystemExit:
        # On argument error
        return 2

    except Exception as err:
        # On unhandled error
        print(err, file=sys.stderr)
        return 1

    else:
        return 0

    
if __name__ == '__main__':
    sys.exit(main())
