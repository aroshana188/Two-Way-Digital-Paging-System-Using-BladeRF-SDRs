import numpy as np
from gnuradio import gr
import pmt

class rn_debugger(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="RN Debug Print",
            in_sig=None,
            out_sig=None)

        # Input Port: Connect to 'rn_out' of ACK Decoder
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            # 1. Extract Data
            # The ACK Decoder sends a clean PDU with just [RN]
            payload_pmt = pmt.cdr(msg)
            data_list = pmt.u8vector_elements(payload_pmt)
            
            if len(data_list) < 1:
                return

            # 2. Get the Number
            rn_val = data_list[0]

            # 3. Print to Console
            print(f"[TX-SIDE DEBUG] Receiver is asking for Packet #{rn_val}")

        except Exception as e:
            print(f"[RN Debug Error] {e}")