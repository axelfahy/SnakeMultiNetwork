#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket  # Import socket module
import random
from constants import *
from snake_channel import SnakeChannel


class Client(SnakeChannel):
    def __init__(self, ip='127.0.0.1', port=5006):
        super(Client, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        self.ip = ip
        self.port = int(port)
        self.channel.settimeout(2)     # Timeout
        self.connect()

    def connect(self):
        # Num seq = 0xFFFFFFFF
        # 1. Send <<GetToken A Snake>>
        # 2. Wait for <<Token B A ProtocolNumber>>
        # 3. Send <<Connect /nom_cle/val_cle/.../...>>
        # 4. Wait for <<Connected B>>
        state = 0
        A = random.randint(0, (1 << 32) - 1)
        while state < 5:
            try:
                if state == 0:
                    #self.channel.connect((self.ip, self.port))
                    print 'Connect'
                    # 1. Send <<GetToken A Snake>>
                    self.send("GetToken " + str(A) + " Snake", (IP_SERVER, PORT_SERVER), SEQ_OUTBAND)
                    # self.sock.send("GetToken " + str(A) + " Snake")
                    print "OUT   - GetToken ", A, " Snake"
                    state += 1
                elif state == 1:
                    # 2. Wait for <<Token B A ProtocoleNumber>>
                    ack_token, conn = self.receive()
                    print "IN   - ", ack_token
                    if ack_token is None:
                        state = 0
                    else:
                        state += 1

                elif state == 2:
                    token = ack_token.split()
                    # Check if A value is correct
                    if int(token[2]) != int(A):
                        state = 0
                    else:
                        B, proto_number = token[1], token[3]
                        self.send("Connect /challenge/" + str(B) + "/protocol/" + str(proto_number),
                                  (IP_SERVER, PORT_SERVER), SEQ_OUTBAND)
                        print "OUT  - Connect /challenge/", B, "/protocol/", proto_number
                        state += 1

                elif state == 3:
                    ack_connect, conn = self.receive()
                    print "IN   - ", ack_connect
                    if ack_connect is None:
                        state = 2
                    else:
                        token = ack_connect.split()
                        B = token[1]
                        state += 1
                elif state == 4:
                    self.hello_world_message()
                    state += 1

                else:
                    print "Error during connection of client."
            except socket.timeout:
                # If timeout, return to state 0
                state = 0
        return

    def hello_world_message(self):
        for i in range(1, 100):
            self.send(str(self.connections[(IP_SERVER, PORT_SERVER)]) + " Test - Hello World ", (IP_SERVER, PORT_SERVER))

if __name__ == "__main__":
    c = Client(port=5006)

