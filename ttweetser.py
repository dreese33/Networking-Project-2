# Must support up to 5 client connections

from socketserver import ThreadingMixIn
from socket import *
import threading
import argparse


numberOfClients = 0
currentUsers = []
clientInformation = dict()
startServer = True


"""Contains information about client including hashtags, username, thread state, etc"""
class Client:
    def __init__(self, username, socket, thread):
        self.username = username
        self.socket = socket
        self.thread = thread


def addClientStates(username, connectionSocket):
    t = threading.Thread(target=newClient, args=(connectionSocket, address, username)).start()
    connectionSocket.send("username legal, connection established.".encode())
    currentUsers.append(username)
    clientInformation[username] = Client(username, connectionSocket, t)


def removeClientStates(username):
    global numberOfClients
    numberOfClients -= 1

    currentUsers.remove(username)
    del clientInformation[username]
    print("Client " + username + " exited")


def isvalidPort(port):
    if port < 65536 and port > 0:
        return True
    return False


def newClient(clisocket, address, username):
    running = True
    while running:
        try:
            message = clisocket.recv(1024)

            #TODO -- verify message is correct
            #TODO -- parse messages for commands

            msg = message.decode()
            print(msg)
            response = "Received."

            if msg == "exit":
                response = "exit"
                clisocket.send(response.encode())
                removeClientStates(username)
                running = False
                break
            else:
                clisocket.send(response.encode())
        except Exception as exc:
            print("error: exchanging messages with client due to: " + str(exc))
            removeClientStates(username)
            running = False
            break

    clisocket.close()


try:
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="serverPort", type=int)
    options = parser.parse_args()

    serverMessage = ""
    serverPort = options.serverPort
    serverSocket = socket(AF_INET, SOCK_STREAM)
except Exception as err:
    startServer = False
    print("The following exception occurred: " + str(err))


if startServer and not isvalidPort(serverPort):
    startServer = False
    print("error: server port invalid, connection refused.")


if startServer:
    try:
        serverSocket.bind(('', serverPort))
    except Exception as err:
        startServer = False
        print("error: failed to connect to server for unknown reason")


if startServer:
    serverSocket.listen(1)
    print("Server on.")
    while True:
        try:
            connectionSocket, address = serverSocket.accept()
            print("A")
            if numberOfClients < 5:
                username = connectionSocket.recv(1024).decode()
                if username not in currentUsers:
                    numberOfClients += 1
                    print(numberOfClients)
                    addClientStates(username, connectionSocket)
                else:
                    connectionSocket.send("username illegal, connection refused.".encode())
                    connectionSocket.close()
            else:
                print("Extra client")
                connectionSocket.send("error: too many clients".encode())
                connectionSocket.close()
        except Exception as err:
            print("error: something went wrong exchanging messages with client, likely due to client disconnecting" +
                  str(err))

    serverSocket.close()

