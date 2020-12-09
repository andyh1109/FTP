import socket
import tqdm
import os
import argparse
import struct

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 4
# socket type
CONTROL = 0
DATA = 1

#data request type
LIST = 1
GET = 2
SEND = 3
EXIT = 4

#status code
VALID = 1
INVALID = 0

SECRET_LEN = 12

def send_file(s):
    filename = input("Enter file name:\n")
    filesize = os.path.getsize(filename)
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        for _ in progress:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))



def get_file(s):
    filename = input("Enter file name you want to download\n")
    s.send(struct.pack('Q%ds' % len(filename), len(filename), filename.encode()))
    # receive the file infos
    received = s.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for _ in progress:
            bytes_read = s.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))


def list_files(data_socket):
    while True:
        bytes_read = data_socket.recv(struct.calcsize('Q'))
        if not bytes_read:
            break
        filenameLen, = struct.unpack('Q',bytes_read)
        filenameLen = int(filenameLen)
        filename = data_socket.recv(struct.calcsize('%ds' % filenameLen)).decode()
        print(filename)



def connectToServer(host, port):
    s = socket.socket()
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")
    return s;


def login(control_socket):
    control_socket.send(struct.pack('b',CONTROL))
    username = input("Enter username:")
    password = input("Password:")
    loginHeader = struct.pack('QQ', len(username),len(password))
    control_socket.send(loginHeader)
    loginInfo = struct.pack('%ds%ds' % (len(username),len(password)), username.encode(), password.encode())
    control_socket.send(loginInfo)
    validUser, = struct.unpack('b', control_socket.recv(struct.calcsize('b')))
    if(validUser == VALID):
        secret = control_socket.recv(struct.calcsize('%ds' % SECRET_LEN)).decode()
        return secret;
    else:
        print('invalid password or username')
        return -1;


def handle_data_transmit_req(secret):
    select = input("1.List avaliable files in server\n2.Get file from server\n3.Send file to server\n4.Exit\n")
    if(int(select) == EXIT):
        return 0
    data_socket = connectToServer(host, port)
    data_socket.send(struct.pack('b',DATA))
    data_socket.send(secret.encode())
    validSecret, = struct.unpack('b', data_socket.recv(struct.calcsize('b')))
    if(validSecret == INVALID):
        print("invalid secret")
    else:
        print("secret is correct")
        if(int(select) == LIST):
            data_socket.send(struct.pack('b',LIST))
            list_files(data_socket)
        elif(int(select) == GET):
            data_socket.send(struct.pack('b',GET))
            get_file(data_socket)
        elif(int(select) == SEND):
            data_socket.send(struct.pack('b',SEND))
            send_file(data_socket)
            data_socket.close()
        else:
            print("invalid input, please enter 1, 2, 3, or 4")
    
    return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simple File Sender")
    parser.add_argument("host", help="The host/IP address of the receiver")
    parser.add_argument("-p", "--port", help="Port to use, default is 5001", default=5002)
    args = parser.parse_args()
    host = args.host
    port = args.port
    control_socket = connectToServer(host, port)
    secret = login(control_socket)
    keeplooping = 1;
    if(secret != -1):
        while keeplooping:
            keeplooping = handle_data_transmit_req(secret)
    control_socket.close()
   