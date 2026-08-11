import sys
import threading
import time
import datetime
import tkinter as tk
from tkinter import ttk, font
import zmq

# --- GNU RADIO LIBRARY SETUP ---
try:
    import pmt
except ImportError:
    # Adjust path if needed
    sys.path.append(r"C:\Program Files\GNURadio-3.10\lib\site-packages")
    import pmt

# --- CONFIGURATION ---
# Use these ports if running on a different computer. 
# If running on the SAME computer as the Transmitter, change these (e.g., 6666, 6667)
TX_PORT = "tcp://127.0.0.1:6666" 
RX_PORT = "tcp://127.0.0.1:6667" 

class EmergencyDispatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Response System - Mobile Unit")
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
        self.create_control_panel() # Bottom (Includes Dest IP)
        self.create_network_panel() # Top (Includes Source IP)
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
        
        # Red Emergency Button
        style.configure("Emergency.TButton", font=("Segoe UI", 12, "bold"), background="#D32F2F", foreground="white")
        style.map("Emergency.TButton", background=[("active", "#B71C1C")])

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.header_bg, pady=15)
        header_frame.pack(side="top", fill="x")
        
        # UPDATED: Title for Receiver
        title = tk.Label(header_frame, text="🚑 MOBILE UNIT DASHBOARD", bg=self.header_bg, fg="white", font=("Arial Black", 16))
        title.pack()
        # UPDATED: ID for Receiver
        subtitle = tk.Label(header_frame, text="STATUS: ONLINE | UNIT ID: 192.168.1.20", bg=self.header_bg, fg="#BBDEFB", font=("Segoe UI", 9))
        subtitle.pack()

    def create_control_panel(self):
        control_frame = tk.Frame(self.root, bg="#CFD8DC", pady=15, padx=15)
        control_frame.pack(side="bottom", fill="x")

        # --- ROW 1: Options (Priority + Destination IP) ---
        options_frame = tk.Frame(control_frame, bg="#CFD8DC")
        options_frame.pack(fill="x", pady=(0, 5)) 
        
        # Priority Section
        tk.Label(options_frame, text="PRIORITY:", bg="#CFD8DC", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        self.priority_var = tk.StringVar(value="NORMAL")
        prio_menu = ttk.Combobox(options_frame, textvariable=self.priority_var, 
                                 values=["NORMAL", "EMERGENCY"], 
                                 state="readonly", width=12)
        prio_menu.pack(side="left", padx=(5, 20)) 

        # Destination IP Section
        tk.Label(options_frame, text="UNIT ID (DESTINATION ADDRESS):", bg="#CFD8DC", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        self.dst_ip = ttk.Entry(options_frame, width=15, font=("Consolas", 11))
        # UPDATED: Default to Central Command (1.10)
        self.dst_ip.insert(0, "192.168.1.10") 
        self.dst_ip.pack(side="left", padx=5)

        # --- ROW 2: Message Input + Send Button ---
        input_frame = tk.Frame(control_frame, bg="#CFD8DC")
        input_frame.pack(fill="x")

        self.msg_entry = tk.Entry(input_frame, bg="white", fg="black", 
                                  font=("Segoe UI", 12), bd=2, relief="sunken")
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_page())

        send_btn = ttk.Button(input_frame, text="BROADCAST", style="Emergency.TButton", 
                              command=self.send_page, width=15)
        send_btn.pack(side="right")

    def create_network_panel(self):
        # Now only holds the Source IP
        panel = ttk.LabelFrame(self.root, text="DEVICE CONFIGURATION", padding=10)
        panel.pack(side="top", fill="x", padx=15, pady=10)

        # Source
        ttk.Label(panel, text="DEVICE ID (MY ADDRESS):").grid(row=0, column=0, padx=5, sticky="w")
        self.src_ip = ttk.Entry(panel, width=15, font=("Consolas", 11))
        # UPDATED: Default to Mobile Unit IP (1.20)
        self.src_ip.insert(0, "192.168.1.20") 
        self.src_ip.grid(row=0, column=1, padx=5)

    def create_split_log_display(self):
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=15, pady=5)
        
        # --- LEFT: SENT ---
        left_frame = ttk.LabelFrame(container, text="📡 OUTGOING LOG (SENT)", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.sent_log = tk.Text(left_frame, bg="#E1F5FE", fg="black", 
                                font=("Segoe UI Semibold", 11), state="disabled", wrap="word", 
                                padx=10, pady=10, borderwidth=1, relief="solid")
        self.sent_log.pack(side="left", fill="both", expand=True)
        
        scroll_sent = ttk.Scrollbar(left_frame, orient="vertical", command=self.sent_log.yview)
        scroll_sent.pack(side="right", fill="y")
        self.sent_log['yscrollcommand'] = scroll_sent.set

        # --- RIGHT: RECEIVED ---
        right_frame = ttk.LabelFrame(container, text="🚨 INCOMING ALERTS (RECV)", padding=5)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.recv_log = tk.Text(right_frame, bg="#FFFFFF", fg="black", 
                                font=("Segoe UI Semibold", 11), state="disabled", wrap="word", 
                                padx=10, pady=10, borderwidth=1, relief="solid")
        self.recv_log.pack(side="left", fill="both", expand=True)

        scroll_recv = ttk.Scrollbar(right_frame, orient="vertical", command=self.recv_log.yview)
        scroll_recv.pack(side="right", fill="y")
        self.recv_log['yscrollcommand'] = scroll_recv.set

        # --- VISUAL STYLES ---
        self.sent_log.tag_configure("normal", foreground="#01579B") 
        self.recv_log.tag_configure("normal", foreground="#000000") 

        self.sent_log.tag_configure("emergency", foreground="#D50000", font=("Segoe UI", 11, "bold"))
        self.recv_log.tag_configure("emergency", foreground="#D50000", font=("Segoe UI", 11, "bold"))

        self.sent_log.tag_configure("meta", foreground="#555555", font=("Consolas", 9))
        self.recv_log.tag_configure("meta", foreground="#555555", font=("Consolas", 9))

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def log_message(self, text, direction="sent"):
        ts = self.get_timestamp()
        
        # --- PARSING LOGIC FOR INCOMING MESSAGES ---
        # Converts: "[INFO] SRC:192.168.1.10 IP:... MSG:[N] >> hello" 
        # To:       "FROM 192.168.1.10: [N] >> hello"
        if direction == "recv" and "[INFO] SRC:" in text:
            try:
                # 1. Split Header from Content
                if " >> " in text:
                    header_part, content = text.split(" >> ", 1)
                    
                    # 2. Extract Source IP and Priority Tag
                    tokens = header_part.split(" ")
                    src_ip = "UNKNOWN"
                    prio_tag = "[?]"
                    
                    for t in tokens:
                        if t.startswith("SRC:"):
                            src_ip = t.split(":", 1)[1]
                        elif t.startswith("MSG:"):
                            prio_tag = t.split(":", 1)[1]
                            
                    # 3. Reformat
                    text = f"FROM {src_ip}: {prio_tag} >> {content}"
            except Exception:
                # If format is unexpected, just print original
                pass

        # Determine Panel and Prefix
        if direction == "sent":
            target_widget = self.sent_log
            prefix = ">> "
        else:
            target_widget = self.recv_log
            prefix = "<< "

        # Determine Style
        if "[E]" in text:
            style_tag = "emergency"
        else:
            style_tag = "normal"

        target_widget.config(state="normal")
        
        if target_widget.index("end-1c") != "1.0":
            target_widget.insert("end", "\n")

        # Insert
        target_widget.insert("end", f"[{ts}] ", "meta")
        target_widget.insert("end", f"{prefix}{text}\n", style_tag)
            
        target_widget.config(state="disabled")
        target_widget.see("end")

    def send_page(self):
        text = self.msg_entry.get().strip()
        if not text:
            return

        target_ip = self.dst_ip.get()
        source_ip = self.src_ip.get()
        priority_sel = self.priority_var.get()

        if priority_sel == "EMERGENCY":
            prio_code = "E"
        else:
            prio_code = "N"

        # Format: [Code] >> Text
        final_msg = f"[{prio_code}] >> {text}"
        
        full_payload = f"[INFO] SRC:{source_ip} IP:{target_ip} MSG:{final_msg}"
        
        pmt_msg = pmt.cons(pmt.PMT_NIL, pmt.string_to_symbol(full_payload))
        
        try:
            self.tx_socket.send(pmt.serialize_str(pmt_msg))
            self.log_message(f"TO {target_ip}: {final_msg}", "sent")
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            print(f"Transmission Error: {e}")

    def receive_loop(self):
        while self.running:
            try:
                if self.rx_socket.poll(100):
                    msg = self.rx_socket.recv()
                    pmt_obj = pmt.deserialize_str(msg)
                    
                    if pmt.is_pair(pmt_obj):
                         payload = pmt.cdr(pmt_obj)
                    else:
                        payload = pmt_obj

                    if pmt.is_symbol(payload):
                        text = pmt.symbol_to_string(payload)
                    elif pmt.is_u8vector(payload):
                         u8_list = pmt.u8vector_elements(payload)
                         text = "".join([chr(x) for x in u8_list])
                    else:
                        text = str(payload)

                    self.root.after(0, self.log_message, f"{text}", "recv")
                    
            except zmq.ZMQError:
                pass
            except Exception as e:
                print(f"Receive Error: {e}")

    def on_closing(self):
        self.running = False
        self.context.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyDispatchApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
