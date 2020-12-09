import socket
import tqdm
import os
from threading import Thread
import struct


SERVER_HOST = "0.0.0.0"
CONTROL_PORT = 5002
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
RESOURCE_PATH = 'resources/'
# socket type
CONTROL = 0
DATA = 1

#data request type
LIST = 1
GET = 2
SEND = 3


VALID = 1
INVALID = 0

SECRET = 'randomsecret'
SECRET_LEN =12

data_connections = []
control_connections = []
VALID_USERS = {}



# received file from client
def handle_send_request(client_socket):
    # receive the file infos
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    filename = os.path.abspath(os.path.join(os.getcwd(),RESOURCE_PATH, filename))
    # convert to integer
    filesize = int(filesize)
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {os.path.basename(filename)}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for _ in progress:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

def handle_list_request(client_socket):
    files = os.listdir(os.path.join(os.getcwd(),RESOURCE_PATH))
    for f in files:
        filelen = len(f)
        client_socket.send(struct.pack('Q%ds' % filelen, filelen, f.encode()))


# send file to client
def handle_get_request(client_socket):
    filenameLen, = struct.unpack('Q', client_socket.recv(struct.calcsize('Q')))
    filenameLen = int(filenameLen)
    filename = client_socket.recv(struct.calcsize('%ds' % filenameLen)).decode()
    filename = os.path.abspath(os.path.join(os.getcwd(),RESOURCE_PATH, filename))

    filesize = os.path.getsize(filename)
    client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {os.path.basename(filename)}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        for _ in progress:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
    
            client_socket.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))


#TODO
def isValidSecret(userSecret):
    return userSecret == SECRET


def handle_data_request(data_socket):
    userSecret = data_socket.recv(struct.calcsize('%ds' % SECRET_LEN)).decode()
    if(isValidSecret(userSecret)):
        data_socket.send(struct.pack('b',VALID))
        reqType, = struct.unpack('b', data_socket.recv(struct.calcsize('b')))
        if(reqType == LIST):
            handle_list_request(client_socket)
            client_socket.close()
        elif(reqType == GET):
            handle_get_request(client_socket)
            client_socket.close()
        elif(reqType == SEND):
            handle_send_request(client_socket)
    else:
        data_socket.send(struct.pack('b',INVALID))


def handle_login_request(control_socket,valid_users):
    login_headinfo = client_socket.recv(struct.calcsize('QQ'))
    usernameLen,pswLen = struct.unpack('QQ', login_headinfo)
    print(usernameLen, pswLen)
    username= client_socket.recv(usernameLen).decode()
    psw = client_socket.recv(pswLen).decode()
    if(username in valid_users and valid_users[username] == psw):
        control_socket.send(struct.pack('b',VALID))
        control_socket.send(SECRET.encode())
    else:
        control_socket.send(struct.pack('b',INVALID))
    

def read_registed_user_to_memory():
    with open("user.txt") as f:
        valid_users = dict(x.rstrip().split(None, 1) for x in f)
    # for i in valid_users:
    #     print(f"user:{i}, pw:{valid_users[i]}")
    return valid_users


if __name__ == "__main__":
    # create the server socket
    # TCP socket
    socket = socket.socket()
    socket.bind((SERVER_HOST, CONTROL_PORT))
    valid_users = read_registed_user_to_memory()
    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    while True:
        socket.listen(5)
        #print(f"[*] Listening as {SERVER_HOST}:{CONTROL_PORT}")
        client_socket, address = socket.accept()
        print(f"[+] {address} is connected.")
        identify_info = client_socket.recv(struct.calcsize('b'))
        print("received")
        msgType, = struct.unpack('b', identify_info)
        if(msgType == CONTROL):
            t = Thread(target=handle_login_request, args=(client_socket, valid_users)).start();
            control_connections.append(t)
        elif(msgType == DATA):
            t = Thread(target=handle_data_request, args=(client_socket, )).start();
            data_connections.append(t)

    
    for i in data_connections:
        i.join()
    for i in control_connections:
        i.join()
    socket.close()
