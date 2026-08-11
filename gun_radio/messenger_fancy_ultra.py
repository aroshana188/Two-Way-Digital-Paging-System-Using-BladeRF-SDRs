#!/usr/bin/env python3
# Ultra Fancy Chat GUI for GNU Radio Paging System
# Python 3.11 Compatible ✅

import socket, threading, time
import tkinter as tk
from tkinter import ttk
from datetime import datetime

HOST = "127.0.0.1"
TX_PORT = 52001
RX_PORT = 52002

MY_NAME = "Node A 🧑‍💻"
REMOTE_NAME = "Node B 🛰️"

RECONNECT_DELAY = 1.5

# ---------------- SOCKET CLIENT ----------------
class SocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False

    def connect(self):
        if self.connected:
            return True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            self.sock = s
            self.connected = True
            return True
        except:
            self.connected = False
            return False

    def send(self, data):
        try:
            if self.connected:
                self.sock.sendall(data)
                return True
        except:
            self.connected = False
        return False

    def recv(self):
        try:
            return self.sock.recv(4096)
        except:
            self.connected = False
            return None

    def close(self):
        try:
            self.sock.close()
        except:
            pass
        self.connected = False


# ---------------- GUI APP ----------------
class FancyMessenger:
    def __init__(self, root):
        self.root = root
        root.title("Paging Communication System")
        root.geometry("560x740")
        root.configure(bg="#ECE5DD")

        # ---------- STATUS BAR ----------
        self.status = tk.StringVar(value="🔴 Connecting to GNU Radio...")
        self.status_bar = tk.Label(
            root, textvariable=self.status, bg="#075E54",
            fg="white", pady=10, font=("Segoe UI", 11, "bold")
        )
        self.status_bar.pack(fill="x")

        # ---------- CHAT CANVAS ----------
        self.canvas = tk.Canvas(root, bg="#ECE5DD", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg="#ECE5DD")

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # ---------- TYPING AREA ----------
        bottom = tk.Frame(root, bg="#F0F0F0", padx=6, pady=6)
        bottom.pack(fill="x")

        self.textbox = tk.Text(
            bottom, height=3, font=("Segoe UI", 11),
            wrap="word", padx=10, pady=6
        )
        self.textbox.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.textbox.bind("<Return>", self.enter_to_send)
        self.textbox.bind("<Shift-Return>", lambda e: None)

        self.send_btn = ttk.Button(bottom, text=" SEND 🚀 ", command=self.send_msg)
        self.send_btn.pack(side="right")

        self.textbox.focus()

        # ---------- NETWORK ----------
        self.tx = SocketClient(HOST, TX_PORT)
        self.rx = SocketClient(HOST, RX_PORT)
        self.stop_flag = False

        threading.Thread(target=self.network_manager, daemon=True).start()
        threading.Thread(target=self.rx_loop, daemon=True).start()

    # ---------- CHAT BUBBLES ----------
    def add_message(self, text, side="me"):
        ts = datetime.now().strftime("%H:%M")

        frame = tk.Frame(self.inner, bg="#ECE5DD")

        if side == "me":
            bg = "#DCF8C6"
            name = MY_NAME
            anchor = "e"
            pad = (100,10)
        else:
            bg = "#FFFFFF"
            name = REMOTE_NAME
            anchor = "w"
            pad = (10,100)

        bubble = tk.Label(
            frame,
            text=f"{name}\n{text}\n🕒 {ts}",
            bg=bg,
            wraplength=340,
            justify="left",
            padx=12,
            pady=8,
            font=("Segoe UI", 10)
        )

        bubble.pack(anchor=anchor)
        frame.pack(fill="both", padx=pad, pady=6)

        self.root.after(80, lambda: self.canvas.yview_moveto(1.0))

    # ---------- SEND ----------
    def send_msg(self):
        msg = self.textbox.get("1.0", tk.END).strip()
        if not msg:
            return

        self.add_message(msg, "me")
        self.tx.send((msg + "\n").encode())
        self.textbox.delete("1.0", tk.END)

    # Enter to Send, Shift+Enter new line
    def enter_to_send(self, event):
        self.send_msg()
        return "break"

    # ---------- RECEIVE ----------
    def rx_loop(self):
        while not self.stop_flag:
            if not self.rx.connected:
                time.sleep(0.2)
                continue

            data = self.rx.recv()
            if not data:
                continue

            text = data.decode("utf-8", errors="ignore").strip()
            self.add_message(text, "them")

    # ---------- CONNECTION ----------
    def network_manager(self):
        while not self.stop_flag:
            tx_ok = self.tx.connect()
            rx_ok = self.rx.connect()

            if tx_ok and rx_ok:
                self.status.set("🟢 Online | Paging System Active")
            else:
                self.status.set("🔴 Waiting for GNU Radio...")

            time.sleep(RECONNECT_DELAY)

    def close(self):
        self.stop_flag = True
        self.tx.close()
        self.rx.close()


# ---------------- MAIN ----------------
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
