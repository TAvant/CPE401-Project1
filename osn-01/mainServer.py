#!/usr/bin/python -tt

# mainServer.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 1: Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program1.htm

# imports
import sys, signal, threading
from packages import TCPSocket, Database, ClientThread

# global constants
HOST = '' # reachable by any address the machine has
PORT = 12345

def sysArgs(arguments):
  '''takes a list of system arguments and returns a tuple of the user's ID, 
  server's IP and server's Port number.'''

  # if no args print usage
  if not arguments:
    print 'usage: [--auto] [--manual server_Port]'
    sys.exit()

  # --auto flag
  # uses localhost and port 1234 to test client/server ONLY on same machine
  if arguments[0] == '--auto':
    print 'Server(IP, Port): (localhost, %d)' % (PORT)
    return ('localhost', PORT)

  # --manual flag
  # socket is reachable by any address the machine has by setting
  # the host to ''; the port is given by the user
  if arguments[0] == '--manual':
    print 'Server(IP, Port): (%s, %d)'%(HOST, int(arguments[1]))
    return (HOST, arguments[1])

def handler(signum, frame):
  '''handler for keyboard intrupt, exits main program if Ctrl-C 
  are exectued during program execution.'''

  # print message and exit program
  print '\nKeyboardInterrupt: main server has been terminated.'
  sys.exit()

# main-server
def main():

  # omit first argument from sys args and get server address (host, port)
  address = sysArgs(sys.argv[1:])

  # create server's welcoming socket and initialize
  welcomingSocket = TCPSocket.TCPSocket()
  welcomingSocket.initServerSocket(address)

  # create keyboard intrupt, Ctrl-C, using SIGINT 
  signal.signal(signal.SIGINT, handler)

  # create database object and lock to be used across all threads
  database = Database.Database()
  databaseLock = threading.Lock()

  # create and infinite loop
  while True:

    # accept incoming client connection requests
    clientSocket, clientAddress = welcomingSocket.acceptClientConnection()

    # thread to handle client socket
    clientThread=ClientThread.ClientThread(clientSocket,database,databaseLock)
    clientThread.start()

if __name__ == '__main__':
  main()
