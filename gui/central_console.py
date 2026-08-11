import sys
import threading
import time
import datetime
import tkinter as tk
from tkinter import ttk, font, messagebox
import zmq

# --- GNU RADIO LIBRARY SETUP ---
try:
    import pmt
except ImportError:
    # Adjust path if needed
    sys.path.append(r"C:\Program Files\GNURadio-3.10\lib\site-packages")
    import pmt

# --- CONFIGURATION ---
TX_PORT = "tcp://127.0.0.1:5555" 
RX_PORT = "tcp://127.0.0.1:5557" 

# --- NETWORK DEFINITION ---
MY_FIXED_IP = "192.168.1.10"
USERS = {
    "User 1": "192.168.1.11",
    "User 2": "192.168.1.12",
    "User 3": "192.168.1.13"
}

class CentralConsoleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Response System - Central Console")
        self.root.geometry("900x750") 
        self.root.configure(bg="#E3F2FD") 

        self.setup_styles()

        # --- ZMQ SETUP ---
        self.context = zmq.Context()
        self.tx_socket = self.context.socket(zmq.PUSH)
        self.tx_socket.bind(TX_PORT)
        
        self.rx_socket = self.context.socket(zmq.PULL)
        self.rx_socket.bind(RX_PORT)

        # --- GUI LAYOUT ---
        self.create_header()
        self.create_control_panel() # Bottom
        self.create_network_panel() # Top
        self.create_split_log_display() # Middle

        # --- THREADING ---
        self.running = True
        self.rx_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.rx_thread.start()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        self.bg_color = "#E3F2FD"       
        self.header_bg = "#0D47A1"      
        self.main_font = ("Segoe UI", 11)
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabelframe", background=self.bg_color, foreground="#0D47A1")
        style.configure("TLabelframe.Label", background=self.bg_color, foreground="#0D47A1", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=self.bg_color, foreground="#000000", font=self.main_font)
        style.configure("Emergency.TButton", font=("Segoe UI", 12, "bold"), background="#D32F2F", foreground="white")
        style.map("Emergency.TButton", background=[("active", "#B71C1C")])

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.header_bg, pady=15)
        header_frame.pack(side="top", fill="x")
        title = tk.Label(header_frame, text="🏥 CENTRAL CONSOLE", bg=self.header_bg, fg="white", font=("Arial Black", 16))
        title.pack()
        subtitle = tk.Label(header_frame, text="STATUS: ONLINE | ROLE: DISPATCHER", bg=self.header_bg, fg="#BBDEFB", font=("Segoe UI", 9))
        subtitle.pack()

    def create_network_panel(self):
        panel = ttk.LabelFrame(self.root, text="DISPATCH CONFIGURATION", padding=10)
        panel.pack(side="top", fill="x", padx=15, pady=10)

        # Source IP (Read Only)
        ttk.Label(panel, text="MY ADDRESS (FIXED):").grid(row=0, column=0, padx=5, sticky="w")
        self.src_entry = ttk.Entry(panel, width=20, font=("Consolas", 11))
        self.src_entry.insert(0, MY_FIXED_IP)
        self.src_entry.config(state="readonly") 
        self.src_entry.grid(row=0, column=1, padx=5)

    def create_control_panel(self):
        control_frame = tk.Frame(self.root, bg="#CFD8DC", pady=15, padx=15)
        control_frame.pack(side="bottom", fill="x")

        # --- ROW 1: Options ---
        options_frame = tk.Frame(control_frame, bg="#CFD8DC")
        options_frame.pack(fill="x", pady=(0, 5)) 
        
        # Priority
        tk.Label(options_frame, text="PRIORITY:", bg="#CFD8DC", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.priority_var = tk.StringVar(value="NORMAL")
        prio_menu = ttk.Combobox(options_frame, textvariable=self.priority_var, values=["NORMAL", "EMERGENCY"], state="readonly", width=12)
        prio_menu.pack(side="left", padx=(5, 20)) 

        # Destination Menu (Select User)
        tk.Label(options_frame, text="TARGET USER:", bg="#CFD8DC", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        self.target_var = tk.StringVar()
        # Create list like ["User 1 (192.168.1.11)", ...]
        user_list = [f"{k} ({v})" for k, v in USERS.items()]
        
        self.target_menu = ttk.Combobox(options_frame, textvariable=self.target_var, values=user_list, state="readonly", width=25)
        if user_list: self.target_menu.current(0)
        self.target_menu.pack(side="left", padx=5)

        # --- ROW 2: Input ---
        input_frame = tk.Frame(control_frame, bg="#CFD8DC")
        input_frame.pack(fill="x")
        self.msg_entry = tk.Entry(input_frame, bg="white", fg="black", font=("Segoe UI", 12), bd=2, relief="sunken")
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_page())
        send_btn = ttk.Button(input_frame, text="SEND", style="Emergency.TButton", command=self.send_page, width=15)
        send_btn.pack(side="right")

    def create_split_log_display(self):
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=15, pady=5)
        container.columnconfigure(0, weight=1, uniform="group1")
        container.columnconfigure(1, weight=1, uniform="group1")
        container.rowconfigure(0, weight=1)

        left_frame = ttk.LabelFrame(container, text="📡 OUTGOING LOG", padding=5)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.sent_log = tk.Text(left_frame, bg="#E1F5FE", fg="black", font=("Segoe UI Semibold", 11), state="disabled", wrap="word")
        self.sent_log.pack(side="left", fill="both", expand=True)
        
        right_frame = ttk.LabelFrame(container, text="🚨 INCOMING ALERTS", padding=5)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.recv_log = tk.Text(right_frame, bg="#FFFFFF", fg="black", font=("Segoe UI Semibold", 11), state="disabled", wrap="word")
        self.recv_log.pack(side="left", fill="both", expand=True)

        self.setup_log_tags()

    def setup_log_tags(self):
        for widget in [self.sent_log, self.recv_log]:
            widget.tag_configure("normal", foreground="#01579B") 
            widget.tag_configure("emergency", foreground="#D50000", font=("Segoe UI", 11, "bold"))
            widget.tag_configure("meta", foreground="#555555", font=("Consolas", 9))

    def get_timestamp(self): return datetime.datetime.now().strftime("%H:%M:%S")

    def log_message(self, text, direction="sent"):
        ts = self.get_timestamp()
        
        # Formatting Logic for incoming messages
        if direction == "recv" and "[INFO]" in text:
            try:
                if " >> " in text:
                    header, content = text.split(" >> ", 1)
                    src_ip = "UNKNOWN"
                    parts = header.split(" ")
                    for p in parts:
                        if p.startswith("SRC:"): src_ip = p.split(":")[1]
                    
                    prio = "[N]"
                    if "MSG:[E]" in header: prio = "[E]"
                    elif "MSG:[N]" in header: prio = "[N]"
                    
                    # Map IP back to Name
                    sender_name = src_ip # Default if not found
                    for name, ip in USERS.items():
                        if ip == src_ip: sender_name = name
                        
                    # UPDATED: Only show name
                    text = f"FROM {sender_name}: {prio} >> {content}"
            except: pass 

        target_widget = self.sent_log if direction == "sent" else self.recv_log
        prefix = ">> " if direction == "sent" else "<< "
        style_tag = "emergency" if "[E]" in text else "normal"

        target_widget.config(state="normal")
        if target_widget.index("end-1c") != "1.0": target_widget.insert("end", "\n")
        target_widget.insert("end", f"[{ts}] ", "meta")
        target_widget.insert("end", f"{prefix}{text}\n", style_tag)
        target_widget.config(state="disabled")
        target_widget.see("end")

    def send_page(self):
        text = self.msg_entry.get().strip()
        if not text: return

        # 1. Parse Target Selection "User 1 (192.168.1.11)"
        raw_selection = self.target_var.get()
        if "(" in raw_selection and ")" in raw_selection:
            # Extract IP for network
            target_ip = raw_selection.split("(")[1].split(")")[0]
            # Extract Name for display
            target_name = raw_selection.split(" (")[0]
        else:
            messagebox.showerror("Error", "Invalid Target Selection")
            return

        source_ip = MY_FIXED_IP
        prio_code = "E" if self.priority_var.get() == "EMERGENCY" else "N"

        final_msg = f"[{prio_code}] >> {text}"
        full_payload = f"[INFO] SRC:{source_ip} IP:{target_ip} MSG:{final_msg}"
        pmt_msg = pmt.cons(pmt.PMT_NIL, pmt.string_to_symbol(full_payload))
        
        try:
            self.tx_socket.send(pmt.serialize_str(pmt_msg))
            # UPDATED: Log only the name
            self.log_message(f"TO {target_name}: {final_msg}", "sent")
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            print(f"Transmission Error: {e}")

    def receive_loop(self):
        while self.running:
            try:
                if self.rx_socket.poll(100):
                    msg = self.rx_socket.recv()
                    pmt_obj = pmt.deserialize_str(msg)
                    if pmt.is_pair(pmt_obj): payload = pmt.cdr(pmt_obj)
                    else: payload = pmt_obj
                    
                    if pmt.is_symbol(payload): text = pmt.symbol_to_string(payload)
                    elif pmt.is_u8vector(payload): text = "".join([chr(x) for x in pmt.u8vector_elements(payload)])
                    else: text = str(payload)
                    
                    self.root.after(0, self.log_message, f"{text}", "recv")
            except zmq.ZMQError: pass
            except Exception: pass

    def on_closing(self):
        self.running = False
        self.context.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CentralConsoleApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
