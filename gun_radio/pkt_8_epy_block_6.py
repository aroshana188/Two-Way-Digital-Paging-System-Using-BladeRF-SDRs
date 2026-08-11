"""
Embedded Python Block: ACK Filter (Debounce)
Function: 
1. Filters out rapid, redundant ACKs (ACK Bursts).
2. Allows the same ACK to pass only after a 'timeout' (to handle lost feedback).
"""
import numpy as np
from gnuradio import gr
import pmt
import time

class ack_filter(gr.basic_block):
    def __init__(self, timeout=2.0):
        """
        timeout: Time (seconds) to ignore identical ACKs after passing one.
                 Should be slightly larger than the Receiver's Burst Duration.
        """
        gr.basic_block.__init__(self,
            name="ACK Filter (Debounce)",
            in_sig=None,
            out_sig=None)

        self.timeout = timeout
        
        # State Variables
        self.last_msg_id = -1
        self.last_rn = -1
        self.last_pass_time = 0.0

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            payload = pmt.cdr(msg)
            
            # The input is [MsgID, RN] from Address Filter
            if pmt.is_u8vector(payload):
                data = list(pmt.u8vector_elements(payload))
                
                if len(data) >= 2:
                    msg_id = data[0]
                    rn_num = data[1]
                    
                    current_time = time.time()
                    
                    # --- LOGIC START ---
                    
                    # Condition 1: Is this a DIFFERENT ACK?
                    is_different = (msg_id != self.last_msg_id) or (rn_num != self.last_rn)
                    
                    # Condition 2: Has the timeout expired?
                    time_diff = current_time - self.last_pass_time
                    is_expired = time_diff > self.timeout
                    
                    if is_different or is_expired:
                        # PASS IT
                        self.last_msg_id = msg_id
                        self.last_rn = rn_num
                        self.last_pass_time = current_time
                        
                        self.message_port_pub(pmt.intern("pdu_out"), msg)
                        # Optional Debug
                        # print(f"[ACK Filter] Passing ACK {msg_id}:{rn_num}")
                        
                    else:
                        # DROP IT (It's a repeat within timeout)
                        pass 

        except Exception as e:
            print(f"[ACK Filter] Error: {e}")