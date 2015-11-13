#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import struct
import json

from constants import *


class SnakeChannel(object):

    def __init__(self, channel):
        self.channel = channel
        self.connections = {}
        pass

    def send(self, data, connection, seq=None):
        """Send data with sequence number"""
        if seq is None:  # Incrementation of sequence number (modulo)
            self.connections[connection] = (self.connections[connection] + 1) % (0x1 << 32)
        else:  # Sequence number is 0xFFFFFFFF -> connection packet
            self.connections[connection] = seq

        # Pack (big endian) and send message
        #self.channel.sendto(struct.pack('!I%ds' % (len(data),), self.connections[connection], data), connection)
        self.channel.sendto(json.dumps({'seq': self.connections[connection],
                                        'data': data}), connection)

    def receive(self):
        """Receive data with sequence number"""
        # fromto -> unpack -> check seq number
        # Verification of sequence number

        try:
            data, address = self.channel.recvfrom(BUFFER_SIZE)
            #seq_number, payload = struct.unpack('!Is', data)
            json_data = json.loads(data)
            print json_data
            seq_number, payload = json_data['seq'], json_data['data']
            print "seq : ", seq_number
            print "payload : ", payload
            if self.connections.get(address) is None:
                self.connections[address] = None

            if ((seq_number == SEQ_OUTBAND and self.connections[address] is None) or
                (self.connections[address] < seq_number) or
                (seq_number < self.connections[address] and
                (self.connections[address] - seq_number) > (1 << 31))):
                return payload, address
        except socket.error:
            pass

        return None, None





        #
