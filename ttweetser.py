# Must support up to 5 client connections

from socketserver import ThreadingMixIn
from socket import *
import threading
import argparse


numberOfClients = 0
currentUsers = []
sockets = []
threads = []
startServer = True


def addClientStates(username, connectionSocket):
    t = threading.Thread(target=newClient, args=(connectionSocket, address)).start()
    connectionSocket.send("username legal, connection established.".encode())
    currentUsers.append(username)
    sockets.append(connectionSocket)
    threads.append(t)


def removeClientStates(username):
    print("Client " + username + " exited")
    global numberOfClients
    numberOfClients -= 1

    index = currentUsers.index(username)
    currentUsers.pop(index)
    sockets.pop(index)
    threads.pop(index)


def isvalidPort(port):
    if port < 65536 and port > 0:
        return True
    return False


def newClient(clisocket, address):
    while True:
        message = clisocket.recv(1024)

        #TODO -- verify message is correct
        #TODO -- parse messages for commands

        msg = message.decode()
        print(msg)
        response = "Received."

        if msg == "exit":
            response = "exit"
            clisocket.send(response.encode())

            usernameExit = clisocket.recv(1024).decode()

            removeClientStates(usernameExit)

            break
        else:
            clisocket.send(response.encode())

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
                connectionSocket.send("exit".encode())
                connectionSocket.close()
        except Exception as err:
            print("error: something went wrong exchanging messages with client, likely due to client disconnecting" +
                  str(err))

    serverSocket.close()

