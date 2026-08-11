import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import time

# =========================
# SOCKET CONFIGURATION
# =========================

# MESSAGE PATH
TX_HOST = "127.0.0.1"   # GNU TX Socket PDU (Server)
TX_PORT = 52001

RX_HOST = "0.0.0.0"     # Listening for RX data from GNU RX
RX_PORT = 52002

# ACK PATH
ACK_TX_HOST = "127.0.0.1"
ACK_TX_PORT = 53001

ACK_RX_HOST = "0.0.0.0"
ACK_RX_PORT = 53002

# =========================
# SOCKET SETUP
# =========================

tx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ack_tx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

rx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ack_rx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

rx_sock.bind((RX_HOST, RX_PORT))
rx_sock.listen(1)

ack_rx_sock.bind((ACK_RX_HOST, ACK_RX_PORT))
ack_rx_sock.listen(1)

# =========================
# GUI SETUP
# =========================

root = tk.Tk()
root.title("Paging Messenger with ACK")

chat_box = scrolledtext.ScrolledText(root, width=60, height=20)
chat_box.pack(padx=10, pady=10)

msg_entry = tk.Entry(root, width=50)
msg_entry.pack(side=tk.LEFT, padx=10)

def log(msg):
    chat_box.insert(tk.END, msg + "\n")
    chat_box.see(tk.END)

# =========================
# CONNECT TO GNU TX
# =========================

def connect_tx():
    while True:
        try:
            tx_sock.connect((TX_HOST, TX_PORT))
            ack_tx_sock.connect((ACK_TX_HOST, ACK_TX_PORT))
            log("[SYSTEM] Connected to GNU TX")
            break
        except:
            time.sleep(1)

threading.Thread(target=connect_tx, daemon=True).start()

# =========================
# SEND MESSAGE
# =========================

def send_message():
    msg = msg_entry.get()
    if msg == "":
        return

    tx_sock.send(msg.encode())
    log("[TX] " + msg)
    msg_entry.delete(0, tk.END)

send_btn = tk.Button(root, text="SEND", command=send_message)
send_btn.pack(side=tk.LEFT)

# =========================
# RECEIVE MESSAGE THREAD
# =========================

def receive_messages():
    conn, _ = rx_sock.accept()
    while True:
        try:
            data = conn.recv(1024)
            if data:
                msg = data.decode()
                log("[RX] " + msg)

                # AUTO SEND ACK
                ack = "ACK"
                ack_tx_sock.send(ack.encode())
                log("[SYSTEM] ACK Sent")

        except:
            break

# =========================
# RECEIVE ACK THREAD
# =========================

def receive_ack():
    conn, _ = ack_rx_sock.accept()
    while True:
        try:
            data = conn.recv(1024)
            if data:
                ack = data.decode()
                log("[ACK RECEIVED] " + ack)
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()
threading.Thread(target=receive_ack, daemon=True).start()

root.mainloop()
