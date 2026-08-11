"""
Embedded Python Block: Sequence Number Checker (IP Support)
"""

import numpy as np
from gnuradio import gr
import pmt

class seq_num_checker(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Sequence Num Checker",
            in_sig=None,
            out_sig=None)

        # Register Ports
        self.message_port_register_in(pmt.intern("pdu_in"))
        
        # Output 1: Valid Data (to File Sink)
        self.message_port_register_out(pmt.intern("pdu_out"))
        
        # Output 2: Request/ACK Trigger (to ACK Generator)
        self.message_port_register_out(pmt.intern("request_out"))

        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

        # Internal State
        self.rn = 0  # Expected Sequence Number
        print("[RX Checker] Block Initialized. Waiting for Packet 0.")

    def handle_msg(self, msg):
        if not pmt.is_pdu(msg):
            return

        meta = pmt.car(msg)
        data_pdu = pmt.cdr(msg)
        data_bytes = list(pmt.u8vector_elements(data_pdu))
        
        if len(data_bytes) < 1:
            return 

        # 1. Extract Source IP from Metadata
        # The 'Address & Type Filter' saved this earlier.
        # It is a PMT u8vector (4 bytes).
        src_ip_pmt = pmt.dict_ref(meta, pmt.intern("src_ip"), pmt.PMT_NIL)
        
        if pmt.is_null(src_ip_pmt):
            # Fallback if metadata is missing (shouldn't happen)
            # print("[RX Checker] Error: No Source IP in metadata")
            return

        # 2. Get Sequence Number (First byte of payload)
        sn_received = data_bytes[0]

        # 3. Logic Check
        if sn_received == self.rn:
            # === MATCH: Valid Packet ===
            
            # A. Publish Payload (Strip Sequence Number)
            payload = data_bytes[1:]
            if len(payload) > 0:
                out_vector = pmt.init_u8vector(len(payload), payload)
                out_msg = pmt.cons(meta, out_vector)
                self.message_port_pub(pmt.intern("pdu_out"), out_msg)
            
            # B. Update State
            self.rn = (self.rn + 1) % 256
            
            # C. Send ACK (New RN)
            self.send_ack_request(self.rn, src_ip_pmt)
            
        else:
            # === MISMATCH: Duplicate ===
            # Re-send ACK for the CURRENT RN (Reminder)
            self.send_ack_request(self.rn, src_ip_pmt)

    def send_ack_request(self, req_num, target_ip_pmt):
        """
        Sends a pair: (Target_IP_PMT . Request_Number_Int)
        """
        msg_pair = pmt.cons(target_ip_pmt, pmt.from_long(req_num))
        self.message_port_pub(pmt.intern("request_out"), msg_pair)