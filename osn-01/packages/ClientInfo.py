#!/usr/bin/python -tt

# ClientInfo.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 1: Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program1.htm

# imports
import datetime

class ClientInfo(object):

  def __init__(self, userInfo, socket=None):
    """initialize user's info (userID, first name, last name), 
    TCP socket, relations, messages and wall posts"""
    self.userInfo = userInfo
    self.socket = socket
    self.friends = []
    self.pending = [] # pending friends
    self.messages = {} # sent messages
    self.received = {} # received messages
    self.posts = {}

  # class getters
  def getUserID(self):
    """returns client's user ID"""
    return self.userInfo[0]

  def getUserName(self):
    """returns client's name as a tuple (first, last)"""
    return tuple(self.userInfo[1:])

  def getSocket(self):
    """returns the clients socket and sets the clients socket to 'None'"""
    sock = self.socket
    self.socket = None
    return sock

  def getFriends(self):
    """returns the clients list of friends"""
    return self.friends

  def getPending(self):
    """returns the list of pending friend requests and clears the list"""
    pendingList = self.pending
    self.pending = []
    return pendingList

  def getReceived(self):
    """returns the dict of messages received and clears the dict"""
    receivedDict = self.received
    self.received = {}
    return receivedDict

  def getPosts(self):
    """returns the dict of key=time and val=post"""
    return self.posts

  # class setters
  def setSocket(self, socket):
    """sets the socket of a client already in the database"""
    self.socket = socket

  def setFriend(self, friend):
    """adds a friend to the clients friend list and returns 'True.' 
    If friend is already in list, returns 'False.'"""

    # return false if friend is already in list
    if friend in self.friends:
      return False

    # else add friend to list and return true
    self.friends.append(friend)
    return True

  def setPending(self, pendingFriend):
    """is a container for pending friend requests, if users is off line."""
    self.pending.append(pendingFriend)

  def setMessage(self, friend, text):
    """appends current message, to a friend, to list of messages
    sent to that friend and returns the current number of messages sent.
    If friend is not in friend list, returns 'False.'"""

    # check if friend is in friend list
    if friend not in self.friends:
      return False

    # check if key is in dict
    if friend not in self.messages:
      self.messages[friend] = []

    # add message to key's [] (val)
    self.messages[friend].append(text)

    # return the length of the message list
    return len(self.messages[friend])

  def setReceived(self, friend, text):
    """appends received message, from a friend, to a list of messages 
    received from that friend."""

    # if the friend is already in the dict
    if friend not in self.received:

      # add friend and message
      self.received[friend] = [text]

    # else, add message to dict (key=friend, val=text)
    else:
      self.received[friend].append(text)


  def setPost(self, group, post):
    """adds the current key=time and val=post to the dict"""
    self.posts[str(datetime.datetime.now())]=(group, self.userInfo[0]+'-'+post)

  def isFriend(self, friend):
    """returns true if friend is in friends list; else returns false"""
    if friend in self.friends:
      return True
    return False

  # class removers
  def removePending(self, pendingFriend):
    """if pending friend exists, removes pending friend from list and 
    returns 'True'; else returns 'False'"""
    if pendingFriend in self.pending:
      del self.pending[self.pending.index(pendingFriend)]
      return True
    return False
