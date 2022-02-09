import time
import struct
import socket
import os
import datetime

# set udp variables
ip_address= input("IP Address:")
if ip_address == None:
    ip_address = "0.0.0.0"
udp_port = 9696


# Clear screen
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# set up udp
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((ip_address, udp_port))

# logging
log_dir = os.path.realpath(__file__)[:-15] + "latency-test-logs"
enable_log = input(f"Save log to {log_dir}? y/n ")
date = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

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

            # printing and saving logs
            print(f"Latency is:\n{time_diff:.4f} seconds\n"
                  f"{(time_diff * 1000):.2f} milliseconds\n"
                  f"{(time_diff / 0.02083333333):.2f} frames (180 degree shutter at 24 fps)\n"
                  f"Stop logging with {'Strg + C' if os.name == 'nt' else 'Strg + X'}")

            if enable_log == "y":

                if not os.path.isdir(log_dir):
                    os.makedirs(log_dir, exist_ok=True)

                with open(f"{log_dir}/latency-test-log-{date}.txt", "a") as f:
                    f.write(f"{time_diff:.4f} seconds\n"
                            f"{(time_diff * 1000):.2f} milliseconds\n"
                            f"{(time_diff / 0.02083333333):.2f} frames (180 degree shutter at 24 fps)\n\n")

            time.sleep(1)
            cls()
except KeyboardInterrupt:
    pass
