"""
Embedded Python Block: ACK Debug Logger
Function: Prints received ACK details to the console.
Input: Expects PDU with payload [MsgID, RN] from Address Filter (ack_out).
"""
import numpy as np
from gnuradio import gr
import pmt
import datetime

class ack_logger(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="ACK Debug Logger",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def handle_msg(self, msg):
        try:
            payload = pmt.cdr(msg)
            
            # The 'ack_out' port from Address Filter sends a PDU of 2 bytes: [MsgID, RN]
            if pmt.is_u8vector(payload):
                data = list(pmt.u8vector_elements(payload))
                
                if len(data) >= 2:
                    msg_id = data[0]
                    rn_num = data[1]
                    timestamp = self.get_timestamp()
                    
                    print(f"[{timestamp}] [ACK RECV] Received ACK for MsgID: {msg_id}, Requesting Next Seq: {rn_num}")
                else:
                    print(f"[ACK Logger] Warning: Received short ACK payload (<2 bytes)")
            
        except Exception as e:
            print(f"[ACK Logger] Error: {e}")