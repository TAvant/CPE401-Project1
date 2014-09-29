#!/usr/bin/python -tt

# client_thread.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 2: P2P Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program2.htm

# imports
import threading, socket, datetime

def cleanReceived(data):
  """function cleanReceived, identifies what the command is and returns the
  command and its data. If the command is bad, function returns empty strings"""

  # get the command
  command = data.split()[0].upper()

  #command is friend [userId]
  if command == 'FRIEND': 
    return command, [data.split()[1]]

  # command is confirm [userId]
  elif command == 'CONFIRM': 
    return command, [data.split()[1]]

  # command is reject [userId]
  elif command == 'REJECT': 
    return command, [data.split()[1]]

  # command is hi [userId]
  elif command == 'HI': 
    return command, [data.split()[1]]

  # command is chat [userId num message]
  elif command == 'CHAT': 
    return command,\
           [data.split()[1], data.split()[2], ' '.join(data.split()[3:])]

  # command is delivered [userId num]
  elif command == 'DELIVERED':
    return command, [data.split()[1], data.split()[2]]

  # command is entries [userId time]
  elif command == 'ENTRIES':
    return command, [data.split()[1], ' '.join(data.split()[2:])]

  # command is wall [userId posts]
  elif command == 'WALL':
    return command, [data.split()[1], data.split()[2:]]

  # then the command is bad, return an empty string and list
  else: return '', []

def friend(udp, data, address, friends, userId, lock):
  """function friend, prompts the user to CONFIRM or REJECT the friend request
  and sends the results back to the requestor. If CONFIRM is choosen the new 
  friend is added to friends."""

  # prompt user to reject or confirm friend request
  s1 = data[0] + " has requested friendship: press 'c' to confirm\n" 
  s2 = '(followed by enter) or any other key to reject the friendship.\n>> '
  verdict = raw_input(s1+s2)

  # if confirmed send CONFIRM command and add new friend to friends
  if verdict == 'c':
    udp.sendto('CONFIRM ' + userId, address)
    with lock:
      friends[data[0]] = address

  # if rejected send REJECT command
  else: udp.sendto('REJECT ' + userId, address)

def confirm(data, address, friends, lock):
  """function confirm, adds friend who sent friendship confirmation to the 
  dict of friends and prints the confirmation of a friend request for the 
  user to review."""

  # add new friend to friends dict and print message for user
  with lock:
    friends[data[0]] = address
  print 'Friend request has been accecpted by ' + data[0]

def reject(data):
  """function reject, prints the rejection of a friend request for the user
  to review."""
  print 'Friend request has been rejected by ' + data[0]

def hi(data, address, friends, lock):
  """function hi, updates a friends address information in the friends dict
  and prints a message to the screen telling the user their friend has come 
  online."""

  # update friend's address information and print message for user
  with lock:
    friends[data[0]] = address
  print data[0] + ' is online'

def chat(udp, data, userId, address):
  """function chat, ouputs chat to screen for the user to view and sends 
  DELIVERED command back to sender."""

  # print chat for user to view and send DELIVERED command
  print data[0] + ' (' + data[1] + ')' + ': ' + data[2]
  udp.sendto('DELIVERED ' + userId + ' ' + data[1], address)

def delivered(data):
  """function delivered, prints delivery confirmation for user to review"""
  print 'delivered chat ' + data[1] + ' to friend ' + data[0] 

def entries(udp, data, address, posts, userId, lock):
  """function entries, sends all posts from the specified time to the 
  requesting friend with command WALL. A message is printed to the screen
  indicating to the user that a friend requested their posts."""

  # check for valid datetime format
  try:
    datetime.datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S')

    # put (time: posts) into a list based on the time 
    wallPosts = []
    with lock:
      for key, value in sorted(posts.items()):
        if str(key) <= data[1]:
          wallPosts.append(str(key) + ': ' + value[1])

    # send post to friend and print message to user
    if wallPosts:
      udp.sendto('Wall ' + userId + ' ' + '\n'.join(wallPosts), address)
      print 'sent wall posts to ' + data[0]
    else: udp.sendto('Wall ' + userId + ' no wallpost or none within time.',\
                     address)

  # send an error message if incorrect time is entered
  except ValueError: 
    udp.sendto('WALL ' + userId +\
               ' ERROR: use time format: yyyy-mm-dd hh:mm:ss', address)

def wall(data):
  """function wall, outputs incoming wall post for the user to review."""
  print 'Wallposts (' + data[0] + '):'
  string = data[1][0]
  for item in data[1][1:]:
    if '2014' in item:
      print string
      string = item
    else:
      string += ' ' + item
  print string

class client_thread(threading.Thread):

  def __init__(self, udp, friends, posts, userId, userAddress, lock):
    """initilizes class client_thread's data members:"""
    threading.Thread.__init__(self)
    self.udp = udp
    self.friends = friends
    self.posts = posts
    self.userId = userId
    self.userAddress = userAddress
    self.lock = lock

  def run(self):
    """client_thread handels all incoming udp requests/responses between P2P."""

    # create and infinite loop
    while True:
      
      # listen for incoming datagrams with buffer size of 1024
      data, address = self.udp.recvfrom(1024)

      # get command and its data
      command, data = cleanReceived(data)

      # continue if command is valid
      if command:

        # command is 'FRIEND'
        if command == 'FRIEND': 
          friend(self.udp, data, address, self.friends, self.userId, self.lock)

        # command is 'CONFIRM'
        elif command == 'CONFIRM': 
          confirm(data, address, self.friends, self.lock)

        # command is 'REJECT'
        elif command == 'REJECT': 
          reject(data)

        # command is 'HI'
        elif command == 'HI': 
          hi(data, address, self.friends, self.lock)

        # command is 'CHAT'
        elif command == 'CHAT': 
          chat(self.udp, data, self.userId, address)
  
        # command is 'DELIVERED'
        elif command == 'DELIVERED':
          delivered(data)

        # command is 'ENTRIES'
        elif command == 'ENTRIES': 
          entries(self.udp, data, address, self.posts, self.userId, self.lock)

        # command is 'WALL'
        else: wall(data)

    # close socket
    udp.close()
