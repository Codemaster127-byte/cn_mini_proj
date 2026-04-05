import socket, ssl, threading, random
from protocols import *

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

s = socket.socket()
tls = context.wrap_socket(s, server_hostname=SERVER_IP)
tls.connect((SERVER_IP, TCP_PORT))


def listen():
    while True:
        try:
            data = tls.recv(1024)
            if not data:
                break

            cmd, seq, msg = parse(data)

            if cmd == "DATA":
                # simulate packet loss
                if random.random() < 0.1:
                    print(f"Dropped {seq}")
                    continue

                print(f"Received: {msg}")

                tls.send(make_ack(seq))

        except:
            break


tls.send(make_join())

threading.Thread(target=listen, daemon=True).start()

input("Press Enter to exit...\n")

tls.send(make_leave())
tls.close()