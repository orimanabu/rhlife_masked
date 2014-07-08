#!/usr/bin/python
# vim: set et sts=4 sw=4 ts=4 :
# see also: http://www.slideshare.net/aoshiman/shizuokapy3-totp

import sys
import time
import hashlib
import hmac
import struct
import base64

counter_file = '/path/to/hotp_counter.txt'
secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX====' # from decoded QR code
pin = 'YYYYYYYY'

def get_counter(path):
    f = open(path, 'r')
    line = f.readline()
    return int(line)

def update_counter(path, newval):
    f = open(path, 'w')
    f.write(str(newval) + '\n')

def get_hotp(secret, counter):
    #base_time = int(time.time()) // 30
    #msg = struct.pack('>Q', base_time)
    msg = struct.pack('>Q', int(counter))
    digest = hmac.new(base64.b32decode(secret), msg, hashlib.sha1).digest()
    ob = ord(digest[19])
    pos = ob & 15
    sn = struct.unpack('>I', digest[pos:pos + 4])[0] & 0x7fffffff
    result = '{0:06d}'.format(sn % 10 ** 6)
    return result

if __name__ == '__main__':
    counter = get_counter(counter_file)
#    print '%s%s' % (pin, get_hotp(secret, counter))
    sys.stdout.write(pin + get_hotp(secret, counter))
    update_counter(counter_file, counter + 1)
