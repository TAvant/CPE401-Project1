#!/usr/bin/python -tt

# tcp_socket.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 2: P2P Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program2.htm

# imports
import socket

class tcp_socket(object):

  def __init__(self, sock=None, maxConnections=5, maxMessageSize=1024):
    """Constructor: if no parameter is passed constructor creates
    a socket using IPv4 and TCP protocols; else it uses the 
    socket's (passed) parameters; MAX_CONNECTIONS is set to a max of 5
    unless parameter is overridden"""

    # create a variable for the max number of connections and max message size
    self.maxConnections = maxConnections
    self.maxMessageSize = maxMessageSize

    if not sock:
      # create socket using IPv4 and TCP protocols
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      # SO_REUSEADDR flag tells kernel to reuse a local socket in TIME_WAIT
      # state, without waiting for its natural timeout to expire.
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    else:
      # use current socket's protocols
      self.sock = sock

  def connectToServer(self, serverAddress):
    """clientConnect: connects a client to the server address 
    passed as a parameter; address is a tuple (host, port)"""

    # connect socket to host's address
    self.sock.connect(serverAddress)

  def initServerSocket(self, serverAddress):
    """initServerSocket: establishes and returns a server welcoming socket; 
    member takes a tuple (host, port) as the address"""

    # bind socket to a host and port
    self.sock.bind(serverAddress)

    # queue up to x connection requests
    self.sock.listen(self.maxConnections)

  def acceptClientConnection(self):
    """acceptClientConnection: accepts clients incoming connection request
    and returns a socket for the client and the client's address."""

    # accept incoming client connection requests 
    # and return socket and address
    return self.sock.accept()

  def closeSocket(self):
    """closes the socket"""
    self.sock.close()

  def sendMessage(self, message):
    self.sock.send(message)
    return True

  def receiveMessage(self):
    message = self.sock.recv(1024)
    return message.strip()
