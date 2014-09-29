#!/usr/bin/python -tt

# ClientThread.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 1: Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program1.htm

# imports
import threading, datetime
from packages import TCPSocket

# global constants
VALID_COMMANDS_0 = ('CONFIRM', 'REJECT')
VALID_COMMANDS_1 = ('SEARCH', 'FRIEND', 'CHAT', 'POST', 'ENTRIES', 'QUIT')

def registerClient(sock, data, lock):
  """send message to client asking for their registration information.
  If user's name already exists in database only the socket is updated; 
  else a new user is created. Returns the user's ID."""

  # prompt user to REGISTER
  sock.sendMessage('\nREGISTER WITH SERVER:'\
                   '\n---------------------'\
                   '\nusage-0: [username firstname lastname]')

  # await client response
  userInfo = tuple(sock.receiveMessage().split())

  # add client to database
  with lock:
    data.setClient(userInfo, sock)

  # return the clients userID
  return userInfo[0]

def pendingFriends(userId, sock, data, lock):
  """member check if there are any pending friendship requests and if there
  are gets client to CONFIRM or REJECT the friend request."""

  # check for pending friend requests
  with lock:
    pending = data.isPending(userId)

  # if there are pending, send CONFIRMATION or REJECTION for each
  if pending:
    for requestee in pending:

      # while not valid command
      valid = False
      while not valid:

        # ask client to confirm
        sock.sendMessage('\nUser ' + requestee + ' request your friendship.'
                         '\nENTER VALID COMMAND:'\
                         '\n--------------------'\
                         '\nusage-1: CONFIRM'\
                         '\nusage-2: REJECT')

        # wait to receive valid command
        command = sock.receiveMessage().upper()

        # check for a valid command
        if command in VALID_COMMANDS_0:

          # set valid to true and add friend to list if CONFIRM
          valid = True
          if command == 'CONFIRM':
            with lock:
              data.setClientFriend(userId, requestee)

def receivedMessages (userId, sock, data, lock):
  """gets the clients received messages, if any, and sends them to 
  the client."""

  # get the messages
  with lock:
    messages = data.getClientMessages(userId)

  # if there are messages, send messages to client
  if messages:
    for key in sorted(messages.keys()):

      # send messages to client
      sock.sendMessage('\nUSER '+key.lower()+' HAS SENT YOU A MESSAGE(S):'\
                       '\n---------------------------------'+'-'*len(key)+\
                       '\n' + '\n'.join(messages[key]) +\
                       '\nPRESS ENTER AFTER REVIEWING MESSAGE(S):')

      # wait to receive enter
      sock.receiveMessage()

def getCommand(userId, sock, data, lock):
  """sends a list of valid commands to the client, waits for the client 
  command, and returns the command and additional data as a tuple"""

  # handel pending friend requests
  pendingFriends(userId, sock, data, lock)

  # send any messages received
  receivedMessages (userId, sock, data, lock)

  # loop till valid command is returned
  while True:

    # send list of valid commands
    sock.sendMessage('\nENTER VALID COMMAND OR PRESS ENTER TO REFRESH:'\
                     '\n----------------------------------------------'\
                     '\nusage-1: SEARCH [keyword]'\
                     '\nusage-2: FRIEND [user-id]'\
                     '\nusage-5: CHAT [user-id message]'\
                     '\nusage-6: POST [group message]'\
                     '\nusage-7: ENTRIES [time]'\
                     '\nusage-8: QUIT')

    # wait to receive valid command
    received = sock.receiveMessage()

    # if received, check for a valid command and return the received 
    if received:
      received = tuple(received.split())
      if received[0].upper() in VALID_COMMANDS_1:
        return received

    # return a tuple with the empty string
    return ('',)

def search(keyword, sock, data, lock):
  """member searches the database for a keyword in the client list of
  usernames, first names and last names. The RESULTS [filelength .xml] 
  are sent back to the client."""

  # get the userID's and their first and last names from the database
  with lock:
    clientsInfo = data.getClientsInfo()

  # add clients who have a keywork match as a string to the list of matches
  matches = []
  for clientInfo in clientsInfo:
    if keyword in clientInfo:
      matches.append('\t'.join(clientInfo))
      
  # send list of matches to client
  if matches:
    sock.sendMessage('\nRESULTS FROM SEARCH ' + keyword + ':'\
                     '\n---------------------' + '-' * len(keyword) +\
                     '\nuserID\tfirst\tlast'\
                     '\n' + '\n'.join(matches) +\
                     '\nPRESS ENTER AFTER REVIEWING RESULTS:')
  else:
    sock.sendMessage('\nRESULTS FROM SEARCH ' + keyword + ':'\
                     '\n---------------------' + '-' * len(keyword) +\
                     '\nNO MATCHES FOUND!'\
                     '\nPRESS ENTER AFTER REVIEWING RESULTS:')

  # wait to receive 'enter'
  sock.receiveMessage()

def friend(clientID, potentialFriend, data, lock):
  """adds this clients ID to the potential friends pending list"""

  # if the potential friend exists
  with lock:
    if data.isClient(potentialFriend):

      # add the client to their pending list and return True
      data.setClientFriendRequest(clientID, potentialFriend)
      return True

  # return False if client doesnt exist
  return False

def chat(clientID, friend, message, sock, data, lock):
  """adds a message to a friends received messages dict and send a 
   DELIVERED [friend counter] back to sender."""

  # check if client1 and client2 are friends or if theres no message
  with lock:
    if not data.isFriend(clientID, friend) or not message:
      return False

  # get the chat count and set message to list
  with lock:
    count = data.getChatCounter(clientID, friend, message)
    data.setFriendsMessage(friend, clientID, message)

  # send client confirmation of delivery
  sock.sendMessage('\nDELIVERED CHAT '+str(count)+' TO: '+friend.lower()+\
                   '\nPRESS ENTER TO CONTINUE:')

  # wait to receive 'enter'
  sock.receiveMessage()

  # return success
  return True

def post(clientID, group, text, data, lock):
  """adds clients text to either group F or group FF of their posts dict."""

  # check the parameters
  if text and (group == 'F' or group == 'FF'):

    # set the post to the client's wall and return true
    with lock:
      data.setClientPost(clientID, group, text)
    return True

  # else return false
  return False

def deleteDuplicateFriends(friends, friendsFriends):
  """takes the list of clients friends and the clients friends friends and
  returns a consolidated list of the clients friends friends without any
  duplicates."""

  # check the clients friends aganist the friends friends
  for friend in friends:
    while friend in friendsFriends:
      # remove any of the clients friends from the list of friends friends
      del friendsFriends[friendsFriends.index(friend)]

  # remove any duplicates left in the friends friends and return it
  return list(set(friendsFriends))  

def entries(clientID, time, sock, data, lock):
  """returns up to the 20 most recent wall post of friends and friends of 
  friends, based on the time given by the client: WALL [filelength .xml]"""

  # convert time to one string
  time = time[0] + ' ' + time[1]

  # check for valid datetime format, return false if not correct
  try:
    datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
  except ValueError:
    return False

  # get the userID's of the client's friends and friends of friends
  with lock:
    friends = data.getClientsFriends(clientID)
    friendsFriends = data.getClientsFriendsFriends(clientID)

  # delete any duplicates in the lists F and FF and get one list
  friendsFriends = deleteDuplicateFriends(friends, friendsFriends)

  # get posts of friends marked F and FF and friends friends marked FF
  with lock:
    friendsPosts = data.getClientPosts(True, True, friends)
    friendsFriendsPosts = data.getClientPosts(False, True, friendsFriends)

  # combine all of the post (lists of dicts) together
  dicts = friendsPosts + friendsFriendsPosts
  posts = {}
  for dic in dicts:
    posts.update(dic)

  # convert the sorted posts (dicts) into a list of strings: 'time user post' 
  twentyPlusPosts = []
  for key, value in sorted(posts.items()):
    # ignore any posts where the key is greater than the time
    if key <= time:
      twentyPlusPosts.append(key + ': ' + value[1])

  # send 20 most recent post based on the time entered by client
  sock.sendMessage('\nTWENTY POST BASED ON TIME ENTERED:'\
                   '\n----------------------------------'\
                   '\n' + '\n'.join(twentyPlusPosts[:20]) + \
                   '\nPRESS ENTER AFTER REVIEWING RESULTS:')

  # wait to receive 'enter'
  sock.receiveMessage()

  # return success
  return True

def quit(userId, data, lock):
  """member takes a user ID, their socket and the database. The user's 
  socket is placed in a list of unused sockets and function returns 'QUIT'."""

  # save the client's socket for later use
  with lock:
    data.setUnusedSocket(userId)

  # return 'QUIT'
  return 'QUIT'

class ClientThread(threading.Thread):

  def __init__(self, clientSocket, database, databaseLock):
    threading.Thread.__init__(self)
    self.clientSocket = TCPSocket.TCPSocket(sock=clientSocket)
    self.database = database
    self.databaseLock = databaseLock

  def run(self):
    """This member handles the interactions between an individual client
    and the server."""

    # register the client
    userID = registerClient(self.clientSocket, self.database, self.databaseLock)
    print  userID, 'has started their client program.'

    # create a loop conditional on client input, break on QUIT
    valid = ''
    while valid != 'QUIT':

      # outputs info to client and waits to receive command from client
      command = getCommand(userID, self.clientSocket,\
                           self.database, self.databaseLock)

      # SEARCH [keyword]
      # client ID1 asking for results matching keyword in register
      if command[0].upper() == 'SEARCH':
        search(command[1], self.clientSocket, self.database, self.databaseLock)

      # FRIEND [user-ID2]
      # client ID1 asking to send friend request to client ID2
      elif command[0].upper() == 'FRIEND':
        friend(userID, command[1], self.database, self.databaseLock)

      # CHAT [user-ID2] [message]
      # client ID1 asking to send chat to client ID2
      elif command[0].upper() == 'CHAT':
        chat(userID, command[1], ' '.join(command[2:]),\
             self.clientSocket, self.database, self.databaseLock)

      # POST [group] [message]
      # client making a post to their wall that is visable to F or FF
      elif command[0].upper() == 'POST':
        post(userID, command[1].upper(), ' '.join(command[2:]),\
             self.database, self.databaseLock)

      # ENTRIES [time]
      # client asking for 20 most current posts (based on time) of F and FF
      elif command[0].upper() == 'ENTRIES':
        entries(userID, command[1:], self.clientSocket,\
                self.database, self.databaseLock)

      # QUIT
      # client asking to be removed from the OSN
      elif command[0].upper() == 'QUIT':
        valid = quit(userID, self.database, self.databaseLock)
        print  userID, 'has terminated their client program.'

      # else do nothing
      else: pass
