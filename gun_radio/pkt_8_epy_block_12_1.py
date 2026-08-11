"""
Embedded Python Block: Priority PDU Mux
"""
import numpy as np
from gnuradio import gr
import pmt
import threading

class priority_mux(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Priority PDU Mux",
            in_sig=None,
            out_sig=None)

        # 1. Register Inputs
        self.message_port_register_in(pmt.intern("data_in"))
        self.message_port_register_in(pmt.intern("ack_in"))
        
        # 2. Register Output
        self.message_port_register_out(pmt.intern("pdu_out"))

        # 3. Bind Handlers
        self.set_msg_handler(pmt.intern("data_in"), self.handle_data)
        self.set_msg_handler(pmt.intern("ack_in"), self.handle_ack)
        
        # Thread lock to prevent race conditions when two packets arrive at once
        self.lock = threading.Lock()

    def handle_ack(self, msg):
        """
        Handler for ACKs (High Priority).
        These usually come from the ACK Generator.
        """
        with self.lock:
            # Pass through immediately
            self.message_port_pub(pmt.intern("pdu_out"), msg)
            # Optional: print("[Mux] Forwarding ACK")

    def handle_data(self, msg):
        """
        Handler for Data Packets (Normal Priority).
        These usually come from PDU Storage -> Add Addressing.
        """
        with self.lock:
            # Pass through immediately
            self.message_port_pub(pmt.intern("pdu_out"), msg)
            # Optional: print("[Mux] Forwarding Data")