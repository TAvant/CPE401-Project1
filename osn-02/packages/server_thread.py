#!/usr/bin/python -tt

# server_thread.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 2: P2P Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program2.htm

# imports
import threading
from packages import tcp_socket

def register(sock, data, lock):
  """send message to client asking for their registration information.
  If user's name already exists in database only the socket is updated; 
  else a new user is created. Returns the user's ID."""

  # prompt user to REGISTER
  sock.sendMessage('\nREGISTER WITH SERVER:'\
                   '\n---------------------'\
                   '\nusage: [username firstname lastname ip port]')

  # await client response
  userInfo = tuple(sock.receiveMessage().split())

  # add client to data: {userid: (first, last, ip, port)}
  with lock:
    data[userInfo[0]] = userInfo[1:]

  # return the clients userID
  return userInfo[0]

def search(keyword, data, lock, sock):
  """function search, searches through the data of each user. If anything is
  matching that users information is sent to the client."""

  # if dict has a matching value add key/values to a list
  matching = []
  with lock:
    for key, values in data.items():
      string = ''
      if keyword in key or keyword in values:
        string = 'keyword (' + keyword + '): ' + key + ' ' 
        for value in values:
          string += value + ' '
        matching.append(string.strip())

  # send list of users matching keyword to client
  if matching:
    sock.sendMessage('\nSEARCH RESULTS:'\
                     '\n---------------'\
                     '\n' + '\n'.join(matching))
  else: sock.sendMessage('\nSEARCH RESULTS:'\
                         '\n---------------'\
                         '\nkeyword doesnot exist: 0 0')

def quit(userid, data, lock):
  """function quit, sets users ip and port numbers to zero and returns True"""
  with lock:
    data[userid] = (data[userid][0], data[userid][1], 0, 0)
  return True

class server_thread(threading.Thread):

  def __init__(self, sock_, data, lock):
    """initilizes class server_thread's data members: sock, data and lock."""
    threading.Thread.__init__(self)
    self.sock = tcp_socket.tcp_socket(sock=sock_)
    self.data = data
    self.lock = lock

  def run(self):
    """member run handels interactions such as server registration and queries
    between the server and client"""

    # register client with server
    userid = register(self.sock, self.data, self.lock)
    print userid, 'is online'

    # create loop conditional user input of QUIT
    exit = False
    while not exit:

      # await query from client
      command = self.sock.receiveMessage().split()

      # if command is 'SEARCH' search server data for keyword and send matche(s)
      if command[0].upper() == 'SEARCH':
        search(command[1], self.data, self.lock, self.sock)

      # if command is 'QUIT' exit this client's thread
      elif command[0].upper() == 'QUIT': 
        exit = quit(userid, self.data, self.lock)
        print userid, 'is offline'

      # else a bad command was entered, just continue
      else: pass
