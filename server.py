#!/usr/bin/env python

import socket

MY_IP = '169.254.175.49'
MESSAGE = b'\x04' + b'\x00' * 9 + socket.inet_aton(MY_IP) + b'\x00' + b'\x00'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("169.254.175.49",35756))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(MESSAGE, ('169.254.255.255', 6996))

MESSAGE = b'\x00\x06\x09\x01' + socket.inet_aton(MY_IP) + b'\x05\x01' + b'\x00' * 5 + 'MDJ-900' + '\x00' * 25
MESSAGE = MESSAGE + b'/opt/0' + b'\x00\x00' + b'0.0.0.0' + b'\x00' * 9 + b'169.254.' + b'\x00' * 32
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(MESSAGE, ('169.254.255.255', 6996))

