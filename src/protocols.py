SERVER_IP = "<SERVER_MACHINE_IP>"
TCP_PORT = 6000   # TLS control
UDP_PORT = 5005   # data

ACK_TIMEOUT = 2
MAX_RETRIES = 3
LOSS_PROB = 0.3


def make_notify(seq, msg):
    return f"NOTIFY|{seq}|{msg}".encode()

def make_ack(seq):
    return f"ACK|{seq}".encode()

def parse_notify(data):
    try:
        parts = data.decode().split("|")
        return int(parts[1]), parts[2]
    except:
        return None, None

def parse_ack(data):
    try:
        return int(data.decode().split("|")[1])
    except:
        return None