import socket
import ssl
import threading
import random
from protocols import *


UDP_PORT_CLIENT = int(input("Enter UDP port: "))

# ---------------- TLS CLIENT (JOIN/LEAVE) ----------------
def send_tls(msg):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    s = socket.socket()
    tls = context.wrap_socket(s, server_hostname=SERVER_IP)
    tls.connect((SERVER_IP, TCP_PORT))

    tls.send(msg.encode())
    tls.close()


# JOIN
send_tls(f"JOIN|{UDP_PORT_CLIENT}")


# ---------------- UDP CLIENT ----------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", UDP_PORT_CLIENT))


def listen():
    while True:
        data, _ = sock.recvfrom(1024)

        seq, msg = parse_notify(data)

        if seq is None:
            continue

        if random.random() < LOSS_PROB:
            print(f"Dropped {seq}")
            continue

        print(f"Received: {msg}")

        sock.sendto(make_ack(seq), (SERVER_IP, UDP_PORT))


threading.Thread(target=listen, daemon=True).start()

input("Press Enter to exit...\n")

# LEAVE
send_tls(f"LEAVE|{UDP_PORT_CLIENT}")