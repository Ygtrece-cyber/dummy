import socket
import time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 4444))
print("Connected!")
try:
    while True:
        data = s.recv(256)
        if data:
            print(data.hex())
        time.sleep(0.1)
except KeyboardInterrupt:
    s.close()
