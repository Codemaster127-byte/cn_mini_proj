# cn_mini_proj
TCP-based group notification system that reliably delivers alerts to multiple subscribers with acknowledgement, retransmission, and timeout handling. Custom packet format with sequence numbers; Group membership management; Loss detection and retransmission; Performance comparison with best-effort UDP


# Reliable Group Notification System (TCP + TLS)

## Overview

This project implements a reliable group notification system using TCP sockets with TLS encryption.
The system allows a server to send notifications to multiple clients, and ensures that each message is acknowledged by the clients.

Although TCP already provides reliable delivery, this project adds an application-level acknowledgement mechanism to confirm that messages are received and processed by clients.

---

## Features

* Multi-client support using threading
* TLS-based secure communication
* Custom protocol for communication
* Message acknowledgement (ACK)
* Retransmission on failure
* Basic group membership (JOIN / LEAVE)

---

## Performance Comparison

### Two modes were tested:

* Best-Effort Mode (No ACK)
* Messages are sent once
* No retransmission
* Observed message loss due to simulated drops
* Reliable Mode (ACK + Retransmission)
* Messages are acknowledged by clients
* Retransmission occurs on failure
* All messages eventually delivered
* Observations:
* Best-effort mode is faster but unreliable
* Reliable mode introduces delay due to retries
* Reliability is significantly improved in ACK mode

## Architecture

The system follows a client-server model.

* **Server**

  * Accepts TLS connections
  * Maintains a list of connected clients
  * Broadcasts notifications to all clients
  * Handles acknowledgements and retransmissions

* **Client**

  * Connects securely using TLS
  * Receives messages from server
  * Sends ACK for each message

---

## Protocol Design

The communication uses a simple text-based protocol:

* `DATA|seq|message` → Notification message
* `ACK|seq` → Acknowledgement
* `JOIN` → Client joins group
* `LEAVE` → Client leaves group

This lightweight format is used for simplicity and easy parsing.

---

## Reliability

Even though TCP ensures delivery, this system implements application-level acknowledgements to ensure that the client has actually received and processed the message.

If an ACK is not received within a timeout, the server retransmits the message (up to 3 attempts).

---

## Security

TLS is used to encrypt communication between client and server.

For simplicity in a controlled environment:

* Certificate verification is disabled on the client side

---

## Concurrency

* The server uses a thread-per-client model
* Each message broadcast is handled in separate threads
* This allows multiple clients to be served concurrently

---

## Setup Instructions

### 1. Generate TLS Certificate

Run the following command:

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

---

### 2. Start Server

```bash
python server.py
```

You should see:

```
[TLS] Server running...
```

---

### 3. Start Client(s)

In separate terminals:

```bash
python client.py
```

---

## Usage

1. Start the server
2. Start multiple clients
3. On the server terminal, type a message:

```
Notification> Hello clients
```

4. Clients will receive the message and send ACKs
5. If a message is not acknowledged, the server retries

---

## Performance Evaluation

The system was tested with multiple clients running simultaneously.

* Multiple clients connected via different terminals
* Messages were broadcast from server
* Clients randomly dropped messages to simulate packet loss
* Retransmission ensured delivery

Observation:

* Messages were successfully delivered after retries
* Latency depends on timeout (2 seconds per retry)

---

## Limitations

* Fixed retry timeout (no dynamic adjustment)
* No message framing (assumes small messages)
* Thread-based model may not scale to very large systems
* Certificate verification is disabled

---

## Conclusion

This project demonstrates:

* Socket programming using TCP
* Secure communication using TLS
* Multi-client handling
* Basic reliability mechanisms

The system successfully meets the requirements of reliable communication and secure data transfer in a networked environment.

---
