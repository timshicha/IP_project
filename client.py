
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
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
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
end = "<END_TOKEN>"

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
OPCODE_JOIN_ROOMS = 9
OPCODE_SEND_MESSAGES = 10

KEEP_ALIVE_INTERVAL = 5

mycolor = random.choice(colors)


# create socket
s = socket.socket()

def get_time():
    return datetime.now().strftime("%H:%M:%S")

    
def show_uses():
    print("\nWelcome to the chat room app!\n")
    print("\tTo set/update your username: username <username>")
    print("\tTo join a room: join room <room name>")
    print("\tTo list rooms: list rooms")
    print("\tTo create room: create room<room name>")
    print("\tTo leave room: leave <room name>")
    print("\tTo list members in a room: list members <room name>")
    print("\tTo list the current rooms you are in: list my rooms")
    print("\tTo send messages to a single room: send <room name> <message>")
    print("\tTo send messages to multiple rooms: send <room names> <message>")


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
            remaining_data = ""
            while(data != ""):
                data = data.split(end, 1)
                if(len(data) > 1):
                    remaining_data = data[1]
                    data = data[0]
                # otherwise element 1 holds message
                data = data.split(sep)
                if(len(data) > 1):
                    print(data[1])
                data = remaining_data


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
show_uses() 


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
        print("\n<Error: Wrong format> Usage: join room room_name\n")
    else:
        to_send = f"{OPCODE_JOIN_ROOM}{sep}{msg[2]}"
        s.send(to_send.encode())

# join rooms
def join_rooms(msg):
    msg = msg.split(" ", 2)
    if(len(msg) < 3):
        print("\n<Error: Wrong format> Usage: join room room_name1 room_name2 ...\n")
    else:
        to_send = f"{OPCODE_JOIN_ROOMS}{sep}{msg[2]}"
        s.send(to_send.encode())

# list members in a room
def list_members(msg):
    msg = msg.split(" ", 2) # ['list', 'members', room_name]
    if(len(msg) < 3):
        print("\n<Error: Wrong format> Usage: list members room_name\n")
    else:
        to_send = f"{OPCODE_LIST_MEMBERS_ROOM}{sep}{msg[2]}"
        s.send(to_send.encode())

# leave a room
def leave_room(msg):
    msg = msg.split(" ", 2) # ['leave', 'room', room_name]
    if(len(msg) < 3):
        print("\n<Error: Wrong format> Usage: leave room room_name\n")
    else:
        to_send = f"{OPCODE_LEAVE_ROOM}{sep}{msg[2]}"
        s.send(to_send.encode())

# send a message to the room
def send(msg):
    msg = msg.split(" ", 2) # ['send', room_name, message]
    if(len(msg) < 3):
        print("\n<Error: Wrong format> Usage: send room_name your_message_here\n")
    else:
        to_send = f"{OPCODE_SEND_MESSAGE}{sep}{msg[1]}{' '}{get_time()}] {mycolor}{msg[2]}{Fore.RESET}"
        s.send(to_send.encode())

# send a message to multiple rooms
def sendm(msg):
    msg = msg.split(" ", 1)
    if(len(msg) < 2):
        print("\n<Error: Wrong format> Usage: sendm (room_name1, room_name2, ...) your_message_here\n")
    else:
        colorized = msg[1].split(")", 1)
        colorized = f"{colorized[0]}{')'}{get_time()}] {mycolor}{colorized[1]}{Fore.RESET}"
        to_send = f"{OPCODE_SEND_MESSAGES}{sep}{colorized}"
        s.send(to_send.encode())


# change your username
def set_username(msg):
    msg = msg.split(" ", 1) # ['nick', new_username]
    if(len(msg) < 2):
        print("\n<Error: Wrong format> Usage: username new_name\n")
    else:
        to_send = f"{OPCODE_SET_USERNAME}{sep}{msg[1]}"
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
    if(msg.startswith("create room ")):
        create_room(msg)

    # list rooms
    elif(msg.startswith("list rooms")):
        list_rooms(msg)

    # list my rooms
    elif(msg.startswith("list my rooms")):
        list_my_rooms(msg)

    # join a room
    elif(msg.startswith("join room ")):
        join_room(msg)

    # list members in group
    elif(msg.startswith("list members ")):
        list_members(msg)

    # leave room
    elif(msg.startswith("leave room ")):
        leave_room(msg)

    # send a message
    elif(msg.startswith("send ")):
        send(msg)

    # join multiple rooms
    elif(msg.startswith("join rooms ")):
        join_rooms(msg)
    # set username
    elif(msg.startswith("username ")):
        set_username(msg)

    # send to multiple rooms
    elif(msg.startswith("sendm ")):
        sendm(msg)

    else:
        print("Command not recognized!\n")


# once the loop exists, we know the server disconnected
print("<The server disconnected>")
# close the socket
s.close()
