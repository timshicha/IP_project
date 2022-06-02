
import socket
from threading import Thread


# server's IP address and port
SERVER_HOST = "0.0.0.0"
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

# disctionary of sockets with their corresponding usernames and rooms
# key is socket name (ie, sender_socket.getsockname())
# value is [username, list of rooms they're in]
client_info = {}

# dictionary of rooms with their corresponding members (as sockets)
# key is room name
# value is a list of sockets in the room
room_info = {}


# create reusable port and listen for connections
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)

print(f"Listening as {SERVER_HOST}:{SERVER_PORT}")

# disconnect client from the server
# remove client from list and from each room
def disconnect_client(client_socket):
    # check that client is in the list
    if(client_socket not in client_info):
        print(f"[Error] Could not disconnect {client_socket.getsockname()}, client socket not found")
        return
    # otherwise remove them from each room
    for i in client_info[client_socket][1]:
        # i is room name
        room_info[i].remove(client_socket)
        # if no one left in room, remove room
        if(len(room_info[i]) == 0):
            del room_info[i]
    # remove the client
    del client_info[client_socket]
    
    print(f"[-] {client_socket.getsockname()} disconnected.")

# safely send a packet (check that socket is connected)
def safe_send(socket_name, message):
    socket_name.send((message+end).encode())

# Call one of the functions below based on user message's opcode
def keep_alive(sender_socket):
    pass

def set_username(sender_socket, username):
    client_info[sender_socket][0] = username

# to create a room
def create_room(sender_socket, room_name):
    to_send = ""
    # if the room name already exists
    if(room_name in room_info):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: a room with name '{room_name}' already exists>\n"
    else:
        # create the room
        room_info[room_name] = [sender_socket] # add client to the room
        client_info[sender_socket][1].append(room_name) # add room to the client
        to_send = f"{OPCODE_SEND_MESSAGE}{sep}\n<You created room {room_name}>\n"
    safe_send(sender_socket, to_send)

# list all the available rooms
def list_rooms(sender_socket):
    to_send = ""
    # if there are no rooms
    if(len(room_info) == 0):
        to_send = f"{OPCODE_SEND_MESSAGE}{sep}\n<There are no rooms>\n"
    else:
        # list the rooms
        rooms = "\nHere are the rooms:\n"
        for i in room_info:
            rooms += ('-' + i + '\n')
        to_send = f"{OPCODE_SEND_MESSAGE}{sep}{rooms}"
    safe_send(sender_socket, to_send)

def list_my_rooms(sender_socket):
    to_send = ""
    # check that the client exists in list of clients
    if(sender_socket not in client_info):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Client not listed>\n"
    else:
        # if client is not in any rooms
        if(len(client_info[sender_socket][1]) == 0):
            to_send = f"{OPCODE_SEND_MESSAGE}{sep}\n<You are not in any rooms>\n"
        # otherwise list the rooms
        else:
            rooms = "\nHere are the room(s) you are in:\n"
            for i in client_info[sender_socket][1]:
                rooms += ('-' + i + '\n')
            to_send = f"{OPCODE_SEND_MESSAGE}{sep}{rooms}"
    safe_send(sender_socket, to_send)

def join_room(sender_socket, room_name):
    to_send = ""
    # check that the client exists in list of clients
    if(sender_socket not in client_info):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Client not listed>\n"
    else:
        # check that the room exists
        if(room_name not in room_info):
            to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Room '{room_name}' doesn't exist>\n"
        # check that the user isn't already in the room
        elif(sender_socket in room_info[room_name]):
            to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: You are already in room '{room_name}'>\n"
        # otherwise add them
        else:
            # add client to room
            room_info[room_name].append(sender_socket)
            # add room to client
            client_info[sender_socket][1].append(room_name)
            to_send = f"{OPCODE_SEND_MESSAGE}{sep}\n<You joined room '{room_name}'\n"
    safe_send(sender_socket, to_send)

def join_rooms(sender_socket, room_names):
    msg = ""
    if(sender_socket not in client_info):
        msg = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Client not listed>\n"
    else:
        # split room into list
        room_names = room_names.split()
        if(len(room_names) == 0):
            msg = f"\nError: Specify a list of rooms>\n"
        else:
            # for each room
            for room_name in room_names:
                # check that the room exists
                if(room_name not in room_info):
                    msg += f"<Error: Room '{room_name}' doesn't exist>\n"
                # check that the user isn't already in the room
                elif(sender_socket in room_info[room_name]):
                    msg += f"<Error: You are already in room '{room_name}'>\n"
                # otherwise add them
                else:
                    # add client to room
                    room_info[room_name].append(sender_socket)
                    # add room to client
                    client_info[sender_socket][1].append(room_name)
                    msg += f"<You joined room '{room_name}'>\n"
    # send the response message
    to_send = f"{OPCODE_SEND_MESSAGE}{sep}{msg}"
    safe_send(sender_socket, to_send)


def list_members(sender_socket, room_name):
    to_send = ""
    # check that the room name exists
    if(room_name not in room_info):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Room '{room_name}' doesn't exist>\n"
    # list the members
    else:
        members = f"\nHere are the members in room '{room_name}':\n"
        for i in room_info[room_name]:
            client_name = client_info[i][0]
            members += ('-' + client_name + '\n')
        to_send = f"{OPCODE_SEND_MESSAGE}{sep}{members}"
    safe_send(sender_socket, to_send)

def leave_room(sender_socket, room_name):
    to_send = ""
    # check that the client exists in list of clients
    if(sender_socket not in client_info):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Client not listed>\n"
    # check that the room is one of client's current rooms
    elif(room_name not in client_info[sender_socket][1]):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: You are not in room '{room_name}'>\n"
    # otherwise remove the client
    else:
        # remove room from client
        client_info[sender_socket][1].remove(room_name)
        # remove client from room
        room_info[room_name].remove(sender_socket)
        # if there is no one in that room now, delete room
        if(len(room_info[room_name]) == 0):
            del room_info[room_name]
        to_send = f"{OPCODE_SEND_MESSAGE}{sep}\n<You left room '{room_name}'>\n"
    safe_send(sender_socket, to_send)

def send(sender_socket, message):
    # parse room name from message
    message = message.split(' ', 1)
    # need at least room name and message
    if(len(message) < 2):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Invalid send message format>\
 Usage: send room_name your_message_here\n"
        safe_send(sender_socket, to_send)
    else:
        room_name, message = message
        # check that the client exists
        if(sender_socket not in client_info):
            to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Client not listed>\n"
            safe_send(sender_socket, to_send)
        # check that the room is listed for the client
        elif(room_name not in client_info[client_socket][1]):
            to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: You are not in room '{room_name}'>\n"
            safe_send(sender_socket, to_send)
        # otherwise broadcast the message
        else:
            to_send = f"{OPCODE_SEND_MESSAGE}{sep}{message}"
            for i in room_info[room_name]:
                safe_send(i, to_send)



# send a message to multiple rooms
def sendm(sender_socket, message):
    room_list = []
    current_room = ""
    open_paren = False
    close_paren = False
    for i in message:
        # if we haven't seen first '('
        if(open_paren == False):
            if(i == ' '): # keep searching, space is ok
                continue
            if(i == '('): # start reading room names
                open_paren = True
                continue
            else:
                to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Bad format>\n"
                safe_send(client_socket, to_send)
                return
        
        # if we're already reading names
        if(i == ')'):
            # stop reading names
            if(current_room != ""): # if we were reading a name
                room_list.append(current_room)
            current_room = ""
            close_paren = True
            break
        # if waiting for new word
        elif(i == ' '):
            if(current_room != ""): # if we were reading a name
                room_list.append(current_room)
                current_room = ""
        # if an alphanumeral
        elif(i.isalnum()):
            # append to the current room name
            current_room += i
        # if some other character, it's illegal
        else:
            to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Invalid character detected>\n"
            safe_send(client_socket, to_send)
            return
    if(close_paren == False):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Bad format, no ')' was detected>\n"
        safe_send(client_socket, to_send)
        return

    # otherwise, send the message to each of the rooms
    # whatever comes after ')' is the message
    message = message.split(')')
    if(len(message) < 2):
        message.append(' ')
    message = message[1] # message to send

    # make sure client exists
    if(sender_socket not in client_info):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\n<Error: Client not listed>\n"
        safe_send(sender_socket, to_send)
        return

    errors = ""
    # for each room
    for room_name in room_list:
        # check that the room is listed under the user
        if(room_name not in client_info[sender_socket][1]):
            errors += f"<Error: You are not in room '{room_name}'>\n"
            continue
        # otherwise broadcast the message
        else:
            to_send = f"{OPCODE_SEND_MESSAGE}{sep}{message}"
            # send to each user in room
            for i in room_info[room_name]:
                safe_send(i, to_send)
    
    # if we racked up any errors, send them to the client
    if(errors != ""):
        to_send = f"{OPCODE_ERROR_MESSAGE}{sep}{errors}"
        safe_send(sender_socket, to_send)

            




# listens for client messages
def listen_for_client(sender_socket):

    # keep listening for incoming messages
    while True:

        # try reading the data
        try:
            data = sender_socket.recv(1024).decode()
        # if client disconnected, remove them
        except Exception as e:
            disconnect_client(sender_socket)
            return
        else:
            # disconnected clients' sockets send blank messages
            if(data == "" or data == None):
                # disconnect user
                disconnect_client(sender_socket)
                # stop listening
                break
            # if it's a legit message from the client
            else:
                # parse the opcode
                data = data.split(sep, 1)
                # make sure there are two fields
                if(len(data) < 2):
                    to_send = f"{OPCODE_ERROR_MESSAGE}{sep}\nError: Bad format>\n"
                    safe_send(sender_socket, to_send)
                    continue

                opcode, message = data
                opcode = int(opcode)

                # call the right function to handle the message
                # keep alive message
                if(opcode == OPCODE_KEEP_ALIVE):
                    keep_alive(sender_socket)

                # set username
                elif(opcode == OPCODE_SET_USERNAME):
                    set_username(sender_socket, message)

                # create room
                elif(opcode == OPCODE_CREATE_ROOM):
                    create_room(sender_socket, message)

                # list all rooms
                elif(opcode == OPCODE_LIST_ROOMS):
                    list_rooms(sender_socket)

                # list rooms the client is in
                elif(opcode == OPCODE_LIST_MY_ROOMS):
                    list_my_rooms(sender_socket)

                # join room
                elif(opcode == OPCODE_JOIN_ROOM):
                    join_room(sender_socket, message)

                # list members in a room
                elif(opcode == OPCODE_LIST_MEMBERS_ROOM):
                    list_members(sender_socket, message)

                # leave a room
                elif(opcode == OPCODE_LEAVE_ROOM):
                    leave_room(sender_socket, message)

                elif(opcode == OPCODE_SEND_MESSAGE):
                    send(sender_socket, message)

                elif(opcode == OPCODE_JOIN_ROOMS):
                    join_rooms(sender_socket, message)

                elif(opcode == OPCODE_SEND_MESSAGES):
                    sendm(sender_socket, message)
                elif(opcode == OPCODE_SET_USERNAME):
                    set_username(sender_socket, message)




# continuously listen for new connections
while True:
    client_socket, client_address = s.accept()

    print(f"[+] {client_address} connected.")

    # add the new client's socket to list of connected clients
    # no name, empty list (since in no rooms)
    client_info[client_socket] = ["Unnamed user", []]

    # start a thread that listens for the client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))

    # end thread when main thread ends
    t.daemon = True
    # start the thread
    t.start()


# when done, close the sockets
for i in client_info:
    i.close()
s.close()
