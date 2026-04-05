SERVER_IP = "10.14.143.142"
TCP_PORT = 6000

def make_data(seq, msg):
    return f"DATA|{seq}|{msg}".encode()

def make_ack(seq):
    return f"ACK|{seq}".encode()

def make_join():
    return b"JOIN"

def make_leave():
    return b"LEAVE"

def parse(data):
    try:
        parts = data.decode().split("|", 2)
        if len(parts) == 1:
            return parts[0], None, None
        elif len(parts) == 2:
            return parts[0], parts[1], None
        return parts[0], parts[1], parts[2]
    except:
        return None, None, None