import socket
import ssl
import threading
import time
from protocols import *

clients = set()
pending = {}

# ---------------- TLS SERVER (JOIN/LEAVE) ----------------
def tls_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    s = socket.socket()
    s.bind((SERVER_IP, TCP_PORT))
    s.listen(5)

    print("[TLS] Control server running...")

    while True:
        conn, addr = s.accept()
        tls_conn = context.wrap_socket(conn, server_side=True)

        data = tls_conn.recv(1024).decode()

        if data.startswith("JOIN"):
            udp_port = int(data.split("|")[1])
            clients.add((addr[0], udp_port))
            print(f"{addr[0]} joined")

        elif data.startswith("LEAVE"):
            udp_port = int(data.split("|")[1])
            clients.discard((addr[0], udp_port))
            print(f"{addr[0]} left")

        tls_conn.close()


# ---------------- UDP SERVER ----------------
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind(("0.0.0.0", UDP_PORT))


def listen_udp():
    while True:
        data, addr = udp_sock.recvfrom(1024)

        if data.startswith(b"ACK"):
            seq = parse_ack(data)
            if (addr, seq) in pending:
                del pending[(addr, seq)]
                print(f"ACK {seq} from {addr}")


def send_with_retry(addr, seq, msg):
    retries = 0

    while retries < MAX_RETRIES:
        udp_sock.sendto(make_notify(seq, msg), addr)
        pending[(addr, seq)] = True

        time.sleep(ACK_TIMEOUT)

        if (addr, seq) not in pending:
            return

        retries += 1
        print(f"Retry {seq} to {addr}")

    print(f"Removing {addr}")
    clients.discard(addr)


def broadcast(msg):
    seq = int(time.time())

    for client in list(clients):
        threading.Thread(
            target=send_with_retry,
            args=(client, seq, msg),
            daemon=True
        ).start()


# ---------------- MAIN ----------------
threading.Thread(target=tls_server, daemon=True).start()
threading.Thread(target=listen_udp, daemon=True).start()

while True:
    msg = input("Notification> ")
    broadcast(msg)