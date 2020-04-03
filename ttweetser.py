# Must support up to 5 client connections

from socketserver import ThreadingMixIn
from socket import *
import threading
import argparse


numberOfClients = 0
clients = []
startServer = True


def isvalidPort(port):
    if port < 65536 and port > 0:
        return True
    return False


def newClient(clisocket, address):
    while True:
        message = clisocket.recv(1024)

        #TODO -- verify message is correct
        #TODO -- parse messages and send appropriate responses

        msg = message.decode()
        print(msg)
        response = "Received."

        if msg == "exit":
            print("Client exited")
            global numberOfClients
            numberOfClients -= 1
            response = "exit"
            clisocket.send(response.encode())
            break
        else:
            clisocket.send(response.encode())

    clisocket.close()


try:
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="serverPort", type=int)
    options = parser.parse_args()

    serverMessage = ""
    serverPort = options.serverPort      # 13402
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
        connectionSocket, address = serverSocket.accept()
        if numberOfClients < 5:
            numberOfClients += 1
            connectionSocket.send("username legal, connection established.".encode())
            print(numberOfClients)
            t = threading.Thread(target=newClient, args=(connectionSocket, address)).start()
            clients.append(1)
        else:
            print("Extra client")
            connectionSocket.send("exit".encode())
            connectionSocket.close()
    serverSocket.close()

