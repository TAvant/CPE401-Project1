#!/usr/bin/python -tt

# mainClient.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 1: Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program1.htm

# imports
import sys
from packages import TCPSocket

# constants
SERVER_HOST = 'localhost'
SERVER_PORT = 12345
USER_NAME = 'userName'

def sysArgs(arguments):
  """takes a list of system arguments and returns a tuple of the user's ID, 
  server's IP and server's Port number."""

  # if no args print usage
  if not arguments:
    print 'usage: [--auto] [--manual user_ID server_IP server_Port]'
    sys.exit()

  # --auto flag
  if arguments[0] == '--auto':
    return (USER_NAME, SERVER_HOST, SERVER_PORT)

  # --manual flag
  if arguments[0] == '--manual':
    return (arguments[1], arguments[2], int(arguments[3]))

# main-client
def main():

  # omit first argument from sys args and get (user ID, server IP, server Port)
  sysInfo = sysArgs(sys.argv[1:])
  userID = sysInfo[0]
  serverAddress = (sysInfo[1], sysInfo[2])

  # create a socket and connect to server
  socket = TCPSocket.TCPSocket()
  socket.connectToServer(serverAddress)

  # REGISTER [user-ID] [user-name] [user-last-name]
  # await/display server instructions, get user input and send back to server
  socket.sendMessage(raw_input(socket.receiveMessage() + '\n>> '))

  # create a loop conditional on user input, break on QUIT
  userInput = ''
  while userInput.upper() != 'QUIT':

    # await/display server insturctions and get user input
    userInput = raw_input(socket.receiveMessage() + '\n>> ')

    # send command to server
    socket.sendMessage(userInput)

  # close the socket
  socket.closeSocket()
  print 'Client program has been terminated.'

if __name__ == '__main__':
  main()
