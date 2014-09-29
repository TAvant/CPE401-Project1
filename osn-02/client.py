#!/usr/bin/python -tt

# client.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 2: P2P Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program2.htm

# imports
import os, sys, select, socket, datetime, threading
from packages import tcp_socket, client_thread

# constants
SERVER_HOST = 'localhost'
SERVER_PORT = 12345
USER_NAME = 'userName'
COMMAND_PROMPT =  '\nENTER VALID COMMAND:'\
                  '\n--------------------'\
                  '\nSEARCH [keyword]'\
                  '\nFRIEND [userid]'\
                  '\nCHAT [userid message]'\
                  '\nPOST [F wallpost] [FF wallpost]'\
                  '\nENTRIES [userid time]'\
                  '\nQUIT'

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

def fileExtract(tcp, friends, chats, posts):
  """function fileExtract, extracts friends, chats and posts information from 
  a file and into dicts: friends{key=userId: val=(ip, port)}, 
  chats{key=userId: val=numChatsSent} and posts{key=time: val=(F or FF, post)}.
  populates dict friends{key=userid: value=(ip, port)} with users current ip 
  and port numbers. Searches to the server are made to get up to date address
  information. """

  # if friends file exists open file and add friends user ids to friends dict
  if os.path.isfile('data/friends'):
    with open('data/friends') as f:
      for userid in f:
        friends[userid] = ('',0)

    # form server, get updated addresses for each friend
    for key in friends:
      tcp.sendMessage('SEARCH ' + key)
      address = tcp.receiveMessage().split()[-2:]
      address = (address[0], int(address[1]))
      friends[key] = (address)

  # if chats file exists open the file and add the data to chats dict
  if os.path.isfile('data/chats'):
    with open('data/chats') as f:
      for line in f:
        key, val = line.split()
        chats[key] = val

  # if posts file exists open the file and add the data to posts dict
  if os.path.isfile('data/posts'):
    with open('data/posts') as f:
      for line in f:
        templist = line.split()
        posts[templist[0]] = (templist[1], ' '.join(templist[2:]))

def hi(udp, userId, friends):
  """function hi: each online friend will be sent a HI command via udp."""

  # got through the dict of friends and if they're online send HI command
  for _, address in friends.items():
    if address[0] and address[1]:
      udp.sendto('HI' + userId, address)

def userinput(time=30.0):
  """"""

  # use select to check if there is anything readable in the buffer
  readable, _, _ = select.select([sys.stdin], [], [], time)

  # anything readable get it up to the endline and return it; else return ''
  if readable:
    return sys.stdin.readline()
  return ''

def cleanInput(userInput):
  """function cleanUserData, identifies what the command is and returns the
  command and its data as a list. If the command is bad, function returns an 
  empty string for command and empty list for data."""

  # get command from user input
  command = userInput.split()[0].upper()

  # command is search [keyword]
  if command == 'SEARCH' and len(userInput.split()) == 2:
    return command, [userInput.split()[1]]

  # command is friend [userId]
  if command == 'FRIEND' and len(userInput.split()) == 2:
    return command, [userInput.split()[1]]

  # command is chat [userId1 message]
  if command == 'CHAT' and len(userInput.split()) >= 3:
    return command, [userInput.split()[1], ' '.join(userInput.split()[2:])]

  # command is post [F or FF, mess]
  if command == 'POST' and len(userInput.split()) >= 3:
    return command, [userInput.split()[1], ' '.join(userInput.split()[2:])]

  # command is entries [userId, time]
  if command == 'ENTRIES' and len(userInput.split()) == 4:
    return command, [userInput.split()[1], ' '.join(userInput.split()[2:])]

  # command is quit
  if command == 'QUIT' and len(userInput.split()) == 1:
    return command, []

  # else the command was bad
  else: return '', []

def search(tcp, data):
  """function search, sends command SEARCH to the server and waits for the 
  servers response. The results are then printed to the terminal for the user
  to view."""

  # send SEARCH keyword to server and print results
  tcp.sendMessage('SEARCH ' + data[0])
  print tcp.receiveMessage()

def friend(tcp, udp, userId, data):
  """function friend, sends a datagram to a specified user, based on the data 
  provided, to request friendship."""

  # from server get address of potential friend
  tcp.sendMessage('SEARCH ' + data[0])
  address = tcp.receiveMessage().split()[-2:]
  address = (address[0], int(address[1]))

  # send friend request
  if address:
    udp.sendto('FRIEND ' + userId, address)
    print 'Sent friend request to ' + data[0]
  else: print 'Could not send friend request to ' + data[0]

def chat(tcp, udp, userId, data, friends, chats):
  """function chat, sends chat datagram to specified user, based on data
  provided. Chat num sent is updated in chats{key=sentto: value=quantity}."""

  # confirm user is a friend
  if data[0] in friends:

    # form server, get updated address for friend
    tcp.sendMessage('SEARCH ' + data[0])
    address = tcp.receiveMessage().split()[-2:]
    address = (address[0], int(address[1]))

    # confirm user is on line
    if address:

      # update chat counter
      if data[0] in chats:
        chats[data[0]] = chats[data[0]] + 1
      else: chats[data[0]] = 1

      # get number of chats
      num = str(chats[data[0]])

      # send message to friend
      udp.sendto('CHAT ' + userId + ' ' + num + ' ' + data[1], address)
      print 'Sent message to ' + data[0]

    # the user is off line
    else: print 'Could not send chat to ' + data[0]

  # the user is not a friend
  else: print 'The following user is not a friend: ' + data[0]

def post(data, posts):
  """function post, adds post to dict posts{key=time: val=(F or FF, post)}"""

  # get current time and add new post and its time to posts dict
  time = datetime.datetime.now()
  posts[time] = (data[0], data[1])
  print 'Added post to wall at ' + str(time)

def entries(tcp, udp, userId, data, friends):
  """function entries, asks for wall posts from a specified time and for 
  friends (F) or firends of friends (FF). A datagram requesting wall posts is 
  sent out to the specified friend. If the request is for friends of friends, 
  that friend will forward the request to their all their friends."""

  # confirm the user is a friend
  if data[0] in friends:

    # form server, get updated address for friend
    tcp.sendMessage('SEARCH ' + data[0])
    address = tcp.receiveMessage().split()[-2:]
    address = (address[0], int(address[1]))

    # confirm user is on line
    if address:

      # send entries request to friend
      udp.sendto('ENTRIES ' + userId + ' ' + data[1], address)
      print 'Sent entries request to ' + data[0]

    # the user is off line
    else: print 'Could not get wall entries of ' + data[0]

  # the user is not a friend
  else: print 'The following user is not a friend: ' + data[0]  

def quit(tcp, userId):
  """function quit, sends command QUIT to server and returns True."""
  tcp.sendMessage('QUIT ' + userId)
  return True

def fileInsert(friends, chats, posts):
  """function fileInsert, outputs all the data from dicts friends, chats and
  posts to file."""

  # check if directory 'data' exists and if not make it
  if not os.path.exists('data'):
    os.mkdir('data')

  # open a file called 'friends' and output each friend's id
  if friends:
    with open('data/friends', 'w') as f:
      for key in friends:
        f.write(key + '\n')

  # open a file called 'chats' and output each friend's id and sent chat number
  if chats:
    with open('data/chats', 'w') as f:
      for key, val in chats.items():
        f.write(key + ' ' + val + '\n')

  # open a file called 'posts' and output each time and wallpost
  if posts:
    with open('data/posts', 'w') as f:
      for key, val in posts.items():
        f.write(str(key) + ' ' + val[0] + ' ' + val[1] + '\n')

# main-client
def main():

  # initialize users data objects
  friends = {}
  chats = {}
  posts = {}

  # omit first argument from sys args and get (user ID, server IP, server Port)
  sysInfo = sysArgs(sys.argv[1:])
  serverAddress = (sysInfo[1], sysInfo[2])

  # create a tcp socket, connect and register with server
  tcp = tcp_socket.tcp_socket()
  tcp.connectToServer(serverAddress)
  userinfo = raw_input(tcp.receiveMessage() + '\n>> ')
  tcp.sendMessage(userinfo)

  # get data from user info (userid, first, last, client ip, client port)
  userId = userinfo.split()[0]
  userAddress = (userinfo.split()[3], int(userinfo.split()[4]))

  # create a udp sending/receiving socket
  udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp.bind(userAddress)

  # get friends, chats and posts from file
  fileExtract(tcp, friends, chats, posts)

  # create thread for incoming requests/responses
  lock = threading.Lock()
  client_thread.client_thread(udp,friends,posts,userId,userAddress,lock).start()

  # update friends addresses and send command HI to all online friends
  hi(udp, userId, friends)

  # show user commands
  print COMMAND_PROMPT

  # create a loop conditional on user input, break on command QUIT
  exit = False
  while not exit:

    # get user input and check it
    userInput = userinput()
    if userInput:

      # get command and its data
      command, data = cleanInput(userInput)

      # continue if command is valid
      if command:

        # command is SEARCH
        if command == 'SEARCH': search(tcp, data)

        # command is FRIEND
        elif command == 'FRIEND': friend(tcp, udp, userId, data)

        # command is CHAT
        elif command == 'CHAT': chat(tcp, udp, userId, data, friends, chats)

        # command is POST
        elif command == 'POST': post(data, posts)

        # command is ENTRIES
        elif command == 'ENTRIES': entries(tcp, udp, userId, data, friends)

        # command is QUIT
        else: exit = quit(tcp, userId)

      # let user know they entered an invalid command
      else: print 'ERROR: invalid command entered.'

  # output friends, chats and posts to file
  fileInsert(friends, chats, posts)

  # close tcp/udp sockets and exit thread
  tcp.closeSocket()
  udp.close()

  # let user know program has terminated
  print 'Client program has been terminated.'

if __name__ == '__main__':
  main()
