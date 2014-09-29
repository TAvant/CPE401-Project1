#!/usr/bin/python -tt

# Database.py

# Copyright 2014 Thomas Avant
# CPE 401 - Programming Assignment 1: Online Social Network
# http://www.cse.unr.edu/~mgunes/cpe401/program1.htm

# imports
from packages import ClientInfo

def findClient(clientID, clients):
  """finds the client in the list of clients and returns it or 
  returns 'None' if client can't be found."""

  # loop through the list of clients to find the client
  for client in clients:

    # if the clients ID's match, return the client
    if clientID == client.getUserID():
      return client

  # returns None if client can't be found
  return None


class Database(object):

  def __init__(self):
    """Initilizes an empty list of clients."""
    self.clients = []
    self.unusedSockets = []

  # class' getters
  def getClientMessages(self, clientID):
    """returns the clients messages as a dict (key=friend, val=[messages])"""

    # get the correct client and return the dict of messages
    client = findClient(clientID, self.clients)
    return client.getReceived()

  def getClientsInfo(self):
    """gathers each clients information into a tuple (clientID, first, last)
    and put all of the tuples into a list to be returned"""

    # loop through all the clients
    clientsInfo = []
    for client in self.clients:

      # add the clients info (tuple) to the list
      clientsInfo.append((client.getUserID(), \
                          client.getUserName()[0], client.getUserName()[1]))

    # return the list
    return clientsInfo

  def getChatCounter(self, userID, friendID, message):
    """gets the count on the number of messages sent to the friend"""

    # find the client and return the count by setting the message
    client = findClient(userID, self.clients)
    return client.setMessage(friendID, message)

  def getClientsFriends(self, clientID):
    """returns the the list of the clients friends"""

    # find the client and return the list of friends
    client = findClient(clientID, self.clients)
    return client.getFriends()

  def getClientsFriendsFriends(self, clientID):
    """returns a list of the client's friends' friends"""

    # find the client and get their list of friends
    client = findClient(clientID, self.clients)
    friends = client.getFriends()

    # get each friends friends
    friendsFriends = []
    for friend in friends:

      # find the friend in the list of clients and add friends to the list
      clientFriend = findClient(friend, self.clients)
      friendsFriends += clientFriend.getFriends()

    # return the list of friends
    return friendsFriends

  def getClientPosts(self, F, FF, clients):
    """depending on the flags F and FF, member returns the post of a 
    client list"""

    # if F and not FF
    if F and not FF:

      # initiilize a list to hold posts (dicts)
      postsList = []

      # for each client in the list of clients
      for client in clients:

        # find the client and get their posts
        theClient = findClient(client, self.clients)
        posts = theClient.getPosts()

        # delete any posts marked with F
        for key, value in posts.items():
          if value[0] == 'F':
            del posts[key]

        # add the client's post marked with an F to the list of posts (dicts)
        postsList.append(posts)

      # return the list of posts (dicts)
      return postsList

    # if not F and FF
    elif not F and FF:

      # initiilize a list to hold posts (dicts)
      postsList = []

      # for each client in the list of clients
      for client in clients:

        # find the client and get their posts
        theClient = findClient(client, self.clients)
        posts = theClient.getPosts()

        # delete any posts marked with FF
        for key, value in posts.items():
          if value[0] == 'FF':
            del posts[key]

        # add the client's post marked with an FF to the list of posts (dicts)
        postsList.append(posts)

      # return the list of posts (dicts)
      return postsList

    # if F and FF
    else:

      # initiilize a list to hold posts (dicts)
      postsList = []

      # for each client in the list of clients
      for client in clients:

        # find the client and get their posts
        theClient = findClient(client, self.clients)
        posts = theClient.getPosts()

        # add the client's post to the list of posts (dicts)
        postsList.append(posts)

      # return the list of posts (dicts)
      return postsList

  # class' setters
  def setClient(self, userInfo, socket):
    """If the client does not exist, new client is added. Else, the current
    socket is added to the client's already existing info."""

    # loop thorugh the clients to see if client already exists
    for client in self.clients:

      # if the client exists, set the clients socket and return true
      if userInfo[0] == client.getUserID() and \
      tuple(userInfo[1:]) == client.getUserName():
        client.setSocket(socket)
        return True

    # else the client doesnt exists and a new client needs to be created
    self.clients.append(ClientInfo.ClientInfo(userInfo, socket))
    return True

  def setClientFriend(self, clientID, friendID):
    """adds clients friend to friend list"""

    # get the correct clients and set them as friends
    client = findClient(clientID, self.clients)
    if friendID not in client.getFriends():
      client.setFriend(friendID)
    friend = findClient(friendID, self.clients)
    if clientID not in friend.getFriends():
      friend.setFriend(clientID)

  def setClientFriendRequest(self, clientID, pendingFriend):
    """adds the potential friend to the clients list of potentials"""

    # get the correct client and set the potential friend
    client = findClient(pendingFriend, self.clients)
    client.setPending(clientID)

  def setClientPost(self, clientID, group, message):
    """sets the clients post to a dict where the key is the time posted
    and the value id a tuple of the group and post"""

    # get the correct client and set their post
    client = findClient(clientID, self.clients)
    client.setPost(group, message)

  def setFriendsMessage(self, friendID, clientID, message):
    """set the message from another client to their firends 
    received messages list"""

    # find the friend and set the message from the client
    friend = findClient(friendID, self.clients)
    friend.setReceived(clientID, message)

  def setUnusedSocket(self, clientID):
    """adds a no longer used socket to a list of unused sockets and 
    sets the client's socket to 'None'"""

    # get the correct client and get the socket to be added to the unused
    client = findClient(clientID, self.clients)
    self.unusedSockets.append(client.getSocket())

  # class' booleans
  def isPending(self, clientID):
    """checks if there are pending friend requests in the list and 
    if there are prints them and returns the list; else returns []."""

    # get the correct client and get the cilents pending list
    client = findClient(clientID, self.clients)
    pending = client.getPending()

    # if list is empty return []
    if not pending:
      return pending

    # return list
    return pending

  def isFriend(self, clientID1, clientID2):
    """returns true if clientID1 is friends with clientID2; 
    else returns false"""

    # get the first and second client
    client1 = findClient(clientID1, self.clients)
    client2 = findClient(clientID2, self.clients)

    # check if clients are friends
    if client1.isFriend(clientID2) and client2.isFriend(clientID1):
      return True

    # else the clients are not friends
    return False

  def isClient(self, clientID):
    """returns true if clientID is in the client list; else returns false"""

    # find the client
    client = findClient(clientID, self.clients)

    # if the client exists return ture
    if client:
      return True

    # else return false
    return False
