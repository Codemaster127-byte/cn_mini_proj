import socket, ssl, threading, time
from protocols import *

ENABLE_ACK = True

clients = set()
clients_lock = threading.Lock()

pending = {}
pending_lock = threading.Lock()

seq = 0
seq_lock = threading.Lock()


def get_seq():
    global seq
    with seq_lock:
        seq += 1
        return seq


def handle_client(conn, addr):
    print(f"[TLS] {addr} connected")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            cmd, seq_id, payload = parse(data)

            if cmd == "JOIN":
                with clients_lock:
                    clients.add(conn)
                print(f"{addr} joined")

            elif cmd == "LEAVE":
                print(f"{addr} left ")

                break

            elif cmd == "ACK":
                with pending_lock:
                    pending.pop((conn, int(seq_id)), None)

    except:
        pass

    finally:
        with clients_lock:
            clients.discard(conn)
        conn.close()


def send_with_retry(client, seq_id, msg):
    retries = 0

    while retries < 3:
        try:
            client.send(make_data(seq_id, msg))

            with pending_lock:
                pending[(client, seq_id)] = True

            time.sleep(2)

            with pending_lock:
                if (client, seq_id) not in pending:
                    return

            retries += 1
            print(f"Retry {seq_id} attempt {retries}")

        except:
            return

    print("Client removed")
    with clients_lock:
        clients.discard(client)


def broadcast(msg):
    seq_id = get_seq()

    with clients_lock:
        for client in list(clients):
            # threading.Thread(
            #     target=send_with_retry,
            #     args=(client, seq_id, msg),
            #     daemon=True
            # ).start()

            if ENABLE_ACK:
                threading.Thread(
                target=send_with_retry,
                args=(client, seq_id, msg),
                daemon=True
            ).start()
            else:
                client.send(make_data(seq_id, msg))
            print(f"Sent seq {seq_id} to {len(clients)} clients")


def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.pem", "key.pem")

    s = socket.socket()
    s.bind(("0.0.0.0", TCP_PORT))
    s.listen(5)

    print("[TLS] Server running...")

    while True:
        conn, addr = s.accept()
        tls_conn = context.wrap_socket(conn, server_side=True)

        threading.Thread(
            target=handle_client,
            args=(tls_conn, addr),
            daemon=True
        ).start()


threading.Thread(target=start_server, daemon=True).start()

while True:
    msg = input("Notification> ")
    broadcast(msg)