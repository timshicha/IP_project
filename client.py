
# client

from http import server
from os import sep
import socket
import random
import time
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back

init()
# user colors
colors = colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]

server_alive = True

# server's IP address and port
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002

# use sep to separate opcode and message
sep = "<SEP>"

# opcodes
OPCODE_ERROR_MESSAGE = -1
OPCODE_KEEP_ALIVE = 0
OPCODE_SET_USERNAME = 1
OPCODE_CREATE_ROOM = 2
OPCODE_LIST_ROOMS = 3
OPCODE_LIST_MY_ROOMS = 4
OPCODE_JOIN_ROOM = 5
OPCODE_LIST_MEMBERS_ROOM = 6
OPCODE_LEAVE_ROOM = 7
OPCODE_SEND_MESSAGE = 8

KEEP_ALIVE_INTERVAL = 5

mycolor = random.choice(colors)

# create socket
s = socket.socket()



# listen for messages from server
def listen_for_messages():
    global server_alive
    # continously listen for messages
    while server_alive:
        data = s.recv(1024).decode()

        # server sends blanks when disconnected
        if(data == None or data == ""):
            server_alive = False
        else:
            data = data.split(sep)
            # otherwise element 1 holds message
            msg = data[1]
            print(msg)


# send a keep alive message
def keepalive(period):
    while server_alive == True:
        to_send = f"{OPCODE_KEEP_ALIVE}{sep}none"
        s.send(to_send.encode())
        time.sleep(period) 


# create TCP socket
print(f"Connecting to {SERVER_HOST}:{SERVER_PORT}...")
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")


# start thread that sends keep alive messages
send_alive_thread = Thread(target=keepalive, args=(KEEP_ALIVE_INTERVAL,))
send_alive_thread.daemon = True
send_alive_thread.start()

# start thread that listens for messages
listen_thread = Thread(target=listen_for_messages)
listen_thread.daemon = True
listen_thread.start()


# The functions below are selected based on what the user commanded
def create_room(msg):
    msg = msg.split(" ", 2) # ['create', 'room', room_name]
    if(len(msg) < 3):
        print("\n<Error: Wrong format> Usage: create room room_name\n")
    else:
        to_send = f"{OPCODE_CREATE_ROOM}{sep}{msg[2]}"
        s.send(to_send.encode())

# list all the rooms
def list_rooms(msg):
    to_send = f"{OPCODE_LIST_ROOMS}{sep}none"
    s.send(to_send.encode())

# list all the rooms the client is in
def list_my_rooms(msg):
    to_send = f"{OPCODE_LIST_MY_ROOMS}{sep}none"
    s.send(to_send.encode())

# join a room
def join_room(msg):
    msg = msg.split(" ", 2) # ['join', 'room', room_name]
    if(len(msg) < 3):
        print("\n<Wrong format>\n")
    else:
        to_send = f"{OPCODE_JOIN_ROOM}{sep}{msg[2]}"
        s.send(to_send.encode())

# list members in a room
def list_members(msg):
    msg = msg.split(" ", 2) # ['list', 'members', room_name]
    if(len(msg) < 3):
        print("\n<Error: Wrong format>\n")
    else:
        to_send = f"{OPCODE_LIST_MEMBERS_ROOM}{sep}{msg[2]}"
        s.send(to_send.encode())

# leave a room
def leave_room(msg):
    msg = msg.split(" ", 2) # ['leave', 'room', room_name]
    if(len(msg) < 3):
        print("\n<Error: Wrong format\n")
    else:
        to_send = f"{OPCODE_LEAVE_ROOM}{sep}{msg[2]}"
        s.send(to_send.encode())

# send a message to the room
def send(msg):
    msg = msg.split(" ", 1) # ['send', room_name + message]
    if(len(msg) < 2):
        print("\n<Error: Wrong format>\n")
    else:
        to_send = f"{OPCODE_SEND_MESSAGE}{sep}{msg[1]}"
        s.send(to_send.encode())


# keep waiting for user input
while server_alive == True:

    # read a message
    msg = input()

    # if server went down while the client entered their input
    if(server_alive == False):
        continue

    if(msg == None or len(msg) == 0):
        continue

    # create a room
    if(msg.startswith("create room")):
        create_room(msg)

    # list rooms
    elif(msg.startswith("list rooms")):
        list_rooms(msg)

    # list my rooms
    elif(msg.startswith("list my rooms")):
        list_my_rooms(msg)

    # join a room
    elif(msg.startswith("join room")):
        join_room(msg)

    # list members in group
    elif(msg.startswith("list members")):
        list_members(msg)

    # leave room
    elif(msg.startswith("leave room")):
        leave_room(msg)

    # send a message
    elif(msg.startswith("send")):
        send(msg)

    else:
        print("Command not recognized!\n")


# once the loop exists, we know the server disconnected
print("<The server disconnected>")
# close the socket
s.close()