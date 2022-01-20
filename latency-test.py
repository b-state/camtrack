import time
import struct
import socket
import os

ip_adress = "127.0.0.1"
udp_port = 9696


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((ip_adress, udp_port))

enable_log = input("Write log? y/n ")

print(f"Stop logging with {'Strg + C' if os.name == 'nt' else 'Strg + X'}")

# Receive-UDP-data event-loop begins here
client.setblocking(False)

try:
    while True:
        newestData = None
        keepReceiving = True

        while keepReceiving:
            try:
                data, fromAddr = client.recvfrom(2048)
                if data:
                    newestData = data
            except socket.error as why:
                if why.args[0] == socket.EWOULDBLOCK:
                    keepReceiving = False
                else:
                    raise why

        if newestData:
            start_time = struct.unpack("1d", newestData)[0]
            end_time = time.time()
            time_diff = end_time - start_time

            print(start_time, end_time, time_diff)

            print(f"Latency is: {time_diff} seconds")
            time.sleep(1)
            cls()
except KeyboardInterrupt:
    pass
