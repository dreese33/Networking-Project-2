# Must support up to 5 client connections

from socketserver import ThreadingMixIn
from socket import *
import threading
import argparse
from collections import defaultdict

# Globals
numberOfClients = 0
clientInformation = dict()
# startServer = True


"""Contains information about client including hashtags, username, thread state, etc"""
class Client:
    def __init__(self, username, socket, thread):
        self.username = username
        self.socket = socket
        self.thread = thread
        self.hashtags = set()
        self.timeline = []
        self.tweets = []

# Adds a client
def addClientStates(username, connectionSocket, address):
    t = threading.Thread(target=newClient, args=(connectionSocket, address, username)).start()
    connectionSocket.send(" username legal, connection established.".encode())
    clientInformation[username] = Client(username, connectionSocket, t)

# Removes a client
def removeClientStates(username):
    global numberOfClients
    numberOfClients -= 1
    del clientInformation[username]
    print("Client " + username + " exited")


def isvalidPort(port):
    return 1024 <= port <= 65535

# Tweet command
def tweet(username, msg):
    try:
        # try splitting up tweet parts
        command, rest = msg.split(' ', 1)
        message, hashtag_str = rest.rsplit(' ', 1)
    except ValueError:
        print('error: invalid tweet command')
        return 'message format illegal.'
    # Extract quotes, check message exists
    if len(message) <= 2 or not ('"' == message[0] == message[-1]) :
        return 'message format illegal.'
    message = message[1:-1]
    # Check message not too big
    if len(message) > 150:
        return 'message length illegal, connection refused.'
    # Check hashtag format is legal
    if len(hashtag_str) < 2 or hashtag_str[0] != '#':
        return 'hashtag illegal format, connection refused.'
    hashtags = hashtag_str[1:].split('#')
    for hashtag in hashtags:
        if len(hashtag) == 0 or hashtag == 'ALL' or not hashtag.isalnum():
            return 'hashtag illegal format, connection refused.'
    # Add message to subscriber timelines
    print(hashtags)
    hashtag_set = set(hashtags)
    for client in clientInformation.values():

        if 'ALL' in client.hashtags \
                    or hashtag_set.intersection(client.hashtags):
            tweet_info = username + ': "' + message + '" ' + hashtag_str
            client.socket.send((' ' + username + ' "' + message + '" ' + hashtag_str).encode())
            print('appending', tweet_info)
            client.timeline.append(tweet_info)
    # Add message to user history
    clientInformation[username].tweets.append(
        username + ': "' + message + '" ' + hashtag_str
    )
    return ''

# Subscribe command
def subscribe(username, msg):
    msg_split = msg.split(' ')
    if len(msg_split) != 2:
        return 'message format illegal.'
    hashtag = msg_split[1]
    if len(hashtag) < 2 or hashtag[0] != '#' or not hashtag[1:].isalnum():
        return 'hashtag illegal format, connection refused.'
    cur_hashtags = clientInformation[username].hashtags
    if hashtag[1:] in cur_hashtags or len(cur_hashtags) == 3:
        return 'operation failed: sub ' + hashtag + ' failed, already exists or exceeds 3 limitation'
    cur_hashtags.add(hashtag[1:])
    return 'operation success'

# Unsubscribe command
def unsubscribe(username, msg):
    msg_split = msg.split(' ')
    if len(msg_split) != 2:
        return 'message format illegal.'
    hashtag = msg_split[1]
    if len(hashtag) < 2 or hashtag[0] != '#':
        return 'hashtag illegal format, connection refused.'
    cur_hashtags = clientInformation[username].hashtags
    if hashtag[1:] == 'ALL':
        cur_hashtags.clear()
        return 'operation success'
    if hashtag[1:] not in cur_hashtags:
        return 'hashtag not found, connection refused.'
    cur_hashtags.remove(hashtag[1:])
    return 'operation success'

# Timeline command
def timeline(username, msg):
    return '\n'.join(clientInformation[username].timeline)

# Getusers command
def getusers(username, msg):
    return '\n'.join(clientInformation.keys())

# Gettweets command
def gettweets(username, msg):
    msg_split = msg.split(' ')
    if len(msg_split) != 2:
        return 'message format illegal.'
    user = msg_split[1]
    if not user in clientInformation:
        return 'no user ' + user + ' in the system'
    return '\n'.join(clientInformation[user].tweets)

# Exit command
def exit(username, msg):
    removeClientStates(username)
    return 'bye bye'

# Main loop for running a client, ran in a thread
def newClient(clisocket, address, username):
    running = True
    while running:
        try:
            message = clisocket.recv(1024)[1:]
            msg = message.decode()
            print('msg rcvd', msg)
            command = msg.split(' ', 1)[0]
            if command == 'tweet':
                response = tweet(username, msg)
            elif command == 'subscribe':
                response = subscribe(username, msg)
            elif command == 'unsubscribe':
                response = unsubscribe(username, msg)
            elif command == 'timeline':
                response = timeline(username, msg)
            elif command == 'getusers':
                response = getusers(username, msg)
            elif command == 'gettweets':
                response = gettweets(username, msg)
            elif command == 'exit':
                response = exit(username, msg)
                running = False
            else:
                response = "Unrecognized command"
            print('sending response', response)
            # Split response in 1023-length chunks
            for start in range(0, len(response), 1023):
                end = start + 1023
                # If there's more to send, prepend +
                if len(response) >= end:
                    prefix = '+'
                # If this is the last message, prepend space
                else:
                    prefix = ' '
                clisocket.send((prefix + response[start:end]).encode())
        except Exception as exc:
            print("error: exchanging messages with client due to: " + str(exc))
            removeClientStates(username)
            running = False
            break

    clisocket.close()

def main():
    global numberOfClients
    # Parse arguments
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(dest="serverPort", type=int)
        options = parser.parse_args()

        serverMessage = ""
        serverPort = options.serverPort
        serverSocket = socket(AF_INET, SOCK_STREAM)
    except Exception as err:
        print("The following exception occurred: " + str(err))
        return

    # Check port
    if not isvalidPort(serverPort):
        print("error: server port invalid, connection refused.")
        return

    # Start Server
    try:
        serverSocket.bind(('', serverPort))
    except Exception as err:
        print("error: failed to connect to server for unknown reason", str(err))
        return

    serverSocket.listen(1)
    print("Server on.")

    # Listen for new connections
    while True:
        try:
            connectionSocket, address = serverSocket.accept()
            if numberOfClients < 5:
                username = connectionSocket.recv(1024).decode()[1:]
                if username not in clientInformation.keys():
                    numberOfClients += 1
                    print('number of clients:', numberOfClients)
                    # Make new client state with new connection
                    addClientStates(username, connectionSocket, address)
                else:
                    connectionSocket.send(" username illegal, connection refused.".encode())
                    connectionSocket.close()
            else:
                print("Extra client")
                connectionSocket.send(" error: too many clients".encode())
                connectionSocket.close()
        except Exception as err:
            print("error: something went wrong exchanging messages with client, likely due to client disconnecting" +
                str(err))

    serverSocket.close()

if __name__ == '__main__':
    main()

