#!/usr/bin/python -tt

# TCPSocket.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 1: Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program1.htm

# imports
import socket

class TCPSocket(object):

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
    """Member uses a fixed length message so connection does not need to be
    broken fter each send and delimiters do not need to be used. Member takes 
    a message up to a max of 1024 chars and sends it. If message is 
    unsuccessful False is returned, indicating the connection has been lost,
    else returns True."""

    # initialize total sent to 0
    totalSent = 0

    # pad the incoming message
    padding = ' ' * (self.maxMessageSize-len(message))
    message += padding

    # loop till message sent is of length 1024
    while totalSent < self.maxMessageSize:

      # send a chunk and get the chunk sent
      sent = self.sock.send(message[totalSent:])
      
      # if nothing is sent, return flase indicating connection is lost
      if not sent:
        return False

      # sum total characters sent
      totalSent += sent

    # return success
    return True

  def receiveMessage(self):
    """Member receives and returns a message of a fixed length, 1024 characters,
    so connection does not need to be broken after each receive and delimiters 
    do not need to be used. If the empty string is returned, the connection has 
    been lost."""

    # initialize message to the empty string
    message = ''

    # loop till message receved is of length 1024
    while len(message) < self.maxMessageSize:

      # get message a chunk at a time
      chunk = self.sock.recv(self.maxMessageSize-len(message))

      # check if the chunk is empty and return the empty string
      if not chunk:
        return chunk

      # concatinate the message with the chunk received
      message += chunk

    # return the message without extra padding
    return message.strip()
