from socket import *
import argparse
import ipaddress
import sys


def checkNumArgs():
    args = len(sys.argv)
    print(args)
    if args != 4:
        return False
    return True


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
    if port < 65536 and port > 0:
        return True
    return False


attemptToConnect = True
if not checkNumArgs():
    attemptToConnect = False
    print("error: args should contain <ServerIP> <ServerPort> <Username>")


if attemptToConnect:
    try:
        args = initialConnectionParse()
    except Exception as err:
        attemptToConnect = False
        print("Argument error - arguments required are ServerIP, Port, Username respectively")


if not isvalidIP(args.serverIP):
    attemptToConnect = False
    print("error: server ip invalid, connection refused.")


if not isvalidPort(args.serverPort) and attemptToConnect:
    attemptToConnect = False
    print("error: server port invalid, connection refused.")


username = args.username
if not username.isalnum() and attemptToConnect:
    attemptToConnect = False
    print("error: username has wrong format, connection refused.")


# Define socket
if attemptToConnect:
    try:
        serverPort = args.serverPort
        serverName = args.serverIP
        username = args.username
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.settimeout(3)
    except Exception as err:
        print("Exception occurred: " + str(err))
        attemptToConnect = False


# Attempt connection to server
sendMessage = True
if attemptToConnect:
    try:
        clientSocket.connect((serverName, serverPort))
        clientSocket.send(username.encode())
    except ConnectionRefusedError:
        print("Connection refused on host " + str(serverName) + ":" + str(serverPort))
        sendMessage = False
    except timeout:
        print("Connection failed due to exceeding the 3 second timeout. " "Client Exiting...")
        sendMessage = False

    except Exception as exc:
        print("Exception occurred connecting to server: " + str(exc))
        sendMessage = False


running = True
if sendMessage:
    while running:
        try:
            response = clientSocket.recv(1024).decode()
            if response == "exit":
                running = False
                print("bye bye")
                break
            elif "illegal" in response:
                running = False
                print(response)
                break
            elif "too many clients" in response:
                running = False
                print(response)
                break
            else:
                print(response)

            val = input()
            clientSocket.send(val.encode())
            if input == "exit":
                running = False
                print("bye bye")
                break
        except KeyboardInterrupt:
            running = False
            clientSocket.send(username.encode())
            print("bye bye")
            break
        except Exception as err:
            print("Exception occurred exchanging messages with server: " + str(err))
    clientSocket.close()

sys.exit()

