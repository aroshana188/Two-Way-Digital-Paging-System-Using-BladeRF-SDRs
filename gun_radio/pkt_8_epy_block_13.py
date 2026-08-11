"""
Embedded Python Block: Decrypted MSG Logger
Function: Prints details + PLAINTEXT content of every incoming packet.
Input: Expects Decrypted PDU (Header + Cleartext Payload).
"""
import numpy as np
from gnuradio import gr
import pmt
import datetime

class msg_logger(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Decrypted MSG Logger",
            in_sig=None,
            out_sig=None)

        # Register Input Port
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def handle_msg(self, msg):
        try:
            payload = pmt.cdr(msg)
            
            if pmt.is_u8vector(payload):
                data = list(pmt.u8vector_elements(payload))
                
                # Header Safety Check (Min 12 bytes)
                if len(data) >= 12:
                    # --- 1. Parse Header ---
                    src_ip = ".".join(map(str, data[4:8]))
                    msg_id = data[9]
                    seq_num = data[10]
                    prio_byte = data[11]
                    prio_char = chr(prio_byte) if prio_byte in [ord('E'), ord('N')] else '?'
                    
                    # --- 2. Parse Payload (Text) ---
                    # Since this is AFTER decryption, bytes 12+ are the message text.
                    raw_text_bytes = data[12:]
                    
                    # Filter out padding (0x00) and non-printable chars
                    clean_text = "".join([chr(b) for b in raw_text_bytes if 32 <= b <= 126])
                    
                    timestamp = self.get_timestamp()
                    
                    # --- 3. Print Log ---
                    print(f"[{timestamp}] [DECRYPTED] From {src_ip} | Seq: {seq_num} | Content: '{clean_text}'")
                else:
                    print(f"[MSG Logger] Warning: Short packet received ({len(data)} bytes)")
            
        except Exception as e:
            print(f"[MSG Logger] Error: {e}")