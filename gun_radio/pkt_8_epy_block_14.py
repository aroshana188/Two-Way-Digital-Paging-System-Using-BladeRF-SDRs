import numpy as np
from gnuradio import gr
import pmt

class ack_checker(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="ACK Packet Debugger",
            in_sig=None,
            out_sig=None)

        # INPUT: Connect to the 'rn_out' of your Sequence Checker
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            # 1. Extract Data
            payload_pmt = pmt.cdr(msg)
            data_list = pmt.u8vector_elements(payload_pmt)
            
            # 2. Safety Check (Must be at least 3 bytes: DST, SRC, RN)
            if len(data_list) < 3:
                print(f"[ACK Debug] Error: Packet too short ({len(data_list)} bytes)")
                return

            # 3. Parse the structure
            # Structure from previous block: [DST, SRC, RN]
            dst_addr = data_list[0]
            src_addr = data_list[1]
            rn_val   = data_list[2]

            # 4. Print Status
            print(f"[ACK OUT] To: Node {dst_addr} | From: Node {src_addr} | Requesting Seq #{rn_val}")

        except Exception as e:
            print(f"[ACK Debug Error] {e}")