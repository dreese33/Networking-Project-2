# Networking-Project-2

Team members: Randal Michnovicz and Dylan Reese

Team name: The Broken Pipes

Work details: Dylan did the network code, Randy did the details of how server responds to client and readme

Run the server this way

python3 ttweetcli.py <ServerPort>

Run the client this way

python3 ttweetcli.py <ServerIP> <ServerPort> <Username>

All libraries used are standard in python 3.

The client can now take terminal input. It will print tweets from sources it is subscribed to.

Client Commands:

* tweet “<150 char max tweet>” <Hashtag>
* subscribe <Hashtag>
* unsubscribe <Hashtag>
* timeline
* getusers
* gettweets <Username>
* exit

Application Protocol:

All messages sent between the client and server are composed to two parts: a 1-byte prefix and payload with a max of 1023 bytes. The prefix '+' shows that there is more data to come as part of a given message, so the client should not print a newline at the end of the message. The prefix ' ' shows that this is the last message in a sequence of messages. All client commands are otherwise sent as typed (with a prefix) and all server responses are sent with a prefix plus what is printed.