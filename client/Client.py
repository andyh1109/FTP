"""
now client can send files to server
"""
import socket
# import tqdm
import os
import argparse

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 4

def send_file(filename, host, port):
    filesize = os.path.getsize(filename)
    s = socket.socket()
    print("[+] Connecting to %s:%d" %(host,port))
    s.connect((host, port))
    print("[+] Connected.")

    # s.send(f"{filename}{SEPARATOR}{filesize}".encode())
    s.send(str("%s%s%d" %(filename,SEPARATOR,filesize)).encode())

    # start sending the file

    # progress = tqdm.tqdm(range(filesize), "Sending %s" %filename, unit="B", unit_scale=True, unit_divisor=1024)
    progress = range(filesize)
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
            # progress.update(len(bytes_read))

    s.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simple File Sender")
    parser.add_argument("file", help="File name to send")
    parser.add_argument("host", help="The host/IP address of the receiver")
    parser.add_argument("-p", "--port", help="Port to use, default is 5001", default=5001)
    args = parser.parse_args()
    filename = args.file
    host = args.host
    port = args.port
    send_file(filename, host, port)
