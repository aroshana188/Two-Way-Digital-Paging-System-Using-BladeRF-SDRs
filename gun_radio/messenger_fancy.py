#!/usr/bin/env python3
# messenger_fancy.py
# Fancy chat GUI (WhatsApp-like) for GNU Radio Socket PDU integration.
# Requires Python 3.8+ (you have 3.11.9) — no extra packages.

import socket, threading, time
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from datetime import datetime

HOST = "127.0.0.1"
TX_PORT = 52001   # connect -> GNU TX server (send)
RX_PORT = 52002   # connect -> GNU RX server (receive)

RECONNECT_DELAY = 1.5

# ---------- Networking helper ----------
class SocketClient:
    def __init__(self, host, port, name="sock"):
        self.host = host
        self.port = port
        self.name = name
        self.sock = None
        self.lock = threading.Lock()
        self.connected = False

    def connect(self):
        with self.lock:
            if self.connected:
                return True
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect((self.host, self.port))
                self.sock = s
                self.connected = True
                return True
            except Exception:
                self.connected = False
                self.sock = None
                return False

    def send(self, data: bytes):
        with self.lock:
            if not self.connected or self.sock is None:
                return False
            try:
                self.sock.sendall(data)
                return True
            except Exception:
                try:
                    self.sock.close()
                except:
                    pass
                self.connected = False
                self.sock = None
                return False

    def recv(self, bufsize=4096):
        with self.lock:
            if not self.connected or self.sock is None:
                return None
            try:
                return self.sock.recv(bufsize)
            except Exception:
                try:
                    self.sock.close()
                except:
                    pass
                self.connected = False
                self.sock = None
                return None

    def close(self):
        with self.lock:
            try:
                if self.sock:
                    self.sock.close()
            except:
                pass
            self.connected = False
            self.sock = None

# ---------- GUI ----------
class FancyMessenger:
    def __init__(self, root):
        self.root = root
        root.title("Paging Messenger — Fancy")
        root.geometry("520x640")
        root.resizable(False, False)

        # Top status bar
        self.status_var = tk.StringVar(value="Connecting...")
        status = ttk.Label(root, textvariable=self.status_var, anchor="center")
        status.pack(fill="x", pady=(4,0))

        # Chat frame (scrollable)
        self.chat_frame = tk.Frame(root, bg="#E5DDD5")
        self.canvas = tk.Canvas(self.chat_frame, bg="#E5DDD5", width=500, height=520, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg="#E5DDD5")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.chat_frame.pack(padx=8, pady=6, fill="both")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Input frame
        bottom = tk.Frame(root)
        bottom.pack(fill="x", padx=8, pady=6)
        self.entry = ttk.Entry(bottom, width=40)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.entry.bind("<Return>", lambda e: self.on_send())
        send_btn = ttk.Button(bottom, text="SEND", command=self.on_send)
        send_btn.pack(side="right")

        # networking
        self.tx_client = SocketClient(HOST, TX_PORT, "TX")
        self.rx_client = SocketClient(HOST, RX_PORT, "RX")
        # start threads
        self.stop_flag = False
        threading.Thread(target=self.network_manager, daemon=True).start()
        threading.Thread(target=self.rx_loop, daemon=True).start()

    # Chat bubble helper
    def add_message(self, text, who="me"):
        # who: 'me' for right side, 'them' for left side
        ts = datetime.now().strftime("%H:%M:%S")
        bubble = tk.Frame(self.inner, bg="#E5DDD5")
        # build bubble label with text + time
        if who == "me":
            bg="#DCF8C6"; anchor="e"; padx=(80,4)
        else:
            bg="#FFFFFF"; anchor="w"; padx=(4,80)
        lbl = tk.Label(bubble, text=text + "\n" + ts, bg=bg, justify="left",
                       wraplength=300, font=("Helvetica", 11), padx=8, pady=6, bd=0)
        lbl.pack(anchor=anchor)
        bubble.pack(fill="both", padx=padx, pady=4)
        # autoscroll to bottom
        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    def on_send(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        # show locally
        self.add_message(msg, who="me")
        # send to TX socket (append newline as simple delimiter)
        data = (msg + "\n").encode("utf-8")
        ok = self.tx_client.send(data)
        if not ok:
            self.add_message("[SYSTEM] send failed — retrying...", who="them")
        self.entry.delete(0, tk.END)

    # Manage connections: keep trying until connected
    def network_manager(self):
        while not self.stop_flag:
            tx_ok = self.tx_client.connect()
            rx_ok = self.rx_client.connect()
            if tx_ok and rx_ok:
                self.status_var.set(f"Connected — TX:{TX_PORT} RX:{RX_PORT}")
            else:
                self.status_var.set("Connecting... (GNU Radio must be running)")
            time.sleep(RECONNECT_DELAY)

    # receive loop: read from rx_client and display messages
    def rx_loop(self):
        while not self.stop_flag:
            if not self.rx_client.connected:
                time.sleep(0.2)
                continue
            data = self.rx_client.recv(4096)
            if not data:
                # disconnected, will be reconnected by manager
                time.sleep(0.2)
                continue
            try:
                text = data.decode("utf-8", errors="ignore").rstrip("\n\r")
            except:
                text = "<binary>"
            # show on left
            self.add_message(text, who="them")

    def close(self):
        self.stop_flag = True
        try:
            self.tx_client.close()
            self.rx_client.close()
        except:
            pass

# ---------- main ----------
def main():
    root = tk.Tk()
    app = FancyMessenger(root)
    def on_close():
        app.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
