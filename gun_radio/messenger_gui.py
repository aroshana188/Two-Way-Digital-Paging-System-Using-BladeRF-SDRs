import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "127.0.0.1"

TX_PORT = 52001   # Python → GNU (GNU is TCP SERVER)
RX_PORT = 52002   # GNU → Python (GNU is TCP SERVER)

# -------------------------------
# SOCKET CONNECTIONS
# -------------------------------
tx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# -------------------------------
# CONNECT TO GNU RADIO
# -------------------------------
def connect_sockets():
    try:
        tx_sock.connect((HOST, TX_PORT))
        print("[SYSTEM] Connected to GNU TX")

        rx_sock.connect((HOST, RX_PORT))
        print("[SYSTEM] Connected to GNU RX")

        status_label.config(text="✅ Connected to GNU Radio")

    except Exception as e:
        status_label.config(text="❌ Connection Failed")
        print("Connection error:", e)

# -------------------------------
# RECEIVE FROM GNU (THREAD)
# -------------------------------
def receive_from_gnu():
    while True:
        try:
            data = rx_sock.recv(4096)
            if not data:
                break

            msg = data.decode("utf-8", errors="ignore")

            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, "RX: " + msg + "\n")
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)

        except:
            break

# -------------------------------
# SEND TO GNU
# -------------------------------
def send_message():
    msg = entry_box.get()

    if msg.strip() == "":
        return

    try:
        tx_sock.sendall((msg + "\n").encode("utf-8"))

        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, "TX: " + msg + "\n")
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)

        entry_box.delete(0, tk.END)

    except:
        status_label.config(text="❌ Send Failed")

# -------------------------------
# GUI SETUP
# -------------------------------
root = tk.Tk()
root.title("Paging Messenger")
root.geometry("500x400")

status_label = tk.Label(root, text="Connecting...", fg="blue")
status_label.pack()

chat_box = scrolledtext.ScrolledText(root, state=tk.DISABLED)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry_box = tk.Entry(root)
entry_box.pack(padx=10, pady=5, fill=tk.X)

send_btn = tk.Button(root, text="SEND", command=send_message)
send_btn.pack(pady=5)

# -------------------------------
# START CONNECTION + RX THREAD
# -------------------------------
connect_sockets()

rx_thread = threading.Thread(target=receive_from_gnu, daemon=True)
rx_thread.start()

root.mainloop()
