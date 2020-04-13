from socket import *
import argparse
import ipaddress
import sys
import threading


def checkNumArgs():
    return len(sys.argv) == 4


def initialConnectionParse():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="serverIP")
    parser.add_argument(dest="serverPort", type=int)
    parser.add_argument(dest="username", type=str)
    return parser.parse_args()


def isvalidIP(address):
    try:
        ipaddress.ip_address(address)
        return True
    except:
        return False


def isvalidPort(port):
    if port < 65536 and port >= 1024:
        return True
    return False


# Loop to recieve and print messages
def listen(clientSocket):
    while True:
        response = clientSocket.recv(1024).decode()
        if response[1:]:
            # If prefix is + then there's more to this response
            if response[0] == '+':
                print(response[1:], end='')
            # If prefix is space then this is the end of this response.
            elif response[0] == ' ':
                print(response[1:])
        if response[1:] == 'bye bye':
            sys.exit()

def main():
    if not checkNumArgs():
        print("error: args should contain <ServerIP>   <ServerPort>   <Username>")
        return

    try:
        args = initialConnectionParse()
    except Exception as err:
        print("error: args should contain <ServerIP>   <ServerPort>   <Username>")
        return

    if not isvalidIP(args.serverIP):
        print("error: server ip invalid, connection refused.")
        return

    if not isvalidPort(args.serverPort):
        print("error: server port invalid, connection refused.")
        return

    username = args.username
    if not username.isalnum():
        print("error: username has wrong format, connection refused.")
        return

    # Define socket
    try:
        serverPort = args.serverPort
        serverName = args.serverIP
        username = args.username
        clientSocket = socket(AF_INET, SOCK_STREAM)
    except Exception as err:
        print("Exception occurred defining socket: " + str(err))
        return

    # Attempt connection to server
    sendMessage = True
    try:
        clientSocket.connect((serverName, serverPort))
        clientSocket.send((' '+username).encode())
        # See whay server said about our attempt to connect
        response = clientSocket.recv(1024).decode()[1:]
        if "illegal" in response:
            print(response)
            return
        elif "too many clients" in response:
            print(response)
            return
        else:
            print(response)
    except ConnectionRefusedError:
        print("connection error, please check your server: Connection refused")
        return
    except timeout:
        print("Connection failed due to exceeding the 3 second timeout. ", "Client Exiting...")
        return
    except Exception as exc:
        print("Exception occurred connecting to server: " + str(exc))
        return

    # Start message recieving in separate thread
    t = threading.Thread(target=listen, args=(clientSocket,)).start()

    # Main loop
    while True:
        message =  input()
        clientSocket.send((' '+message).encode())
    sys.exit()


if __name__ == '__main__':
    main()

