"""
Embedded Python Block: PDU Duplicator
Function: Repeats the input PDU payload N times.
"""
import numpy as np
from gnuradio import gr
import pmt

class pdu_duplicator(gr.basic_block):
    def __init__(self, num_duplicates=3):
        gr.basic_block.__init__(self,
            name="PDU Duplicator",
            in_sig=None,
            out_sig=None)
        
        self.n = num_duplicates

        # Register Ports
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        
        # Bind Handler
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            # 1. Check valid PDU
            if pmt.is_pdu(msg):
                meta = pmt.car(msg)
                vector_data = pmt.cdr(msg)
                
                # 2. Get bytes (Payload + CRC)
                input_bytes = list(pmt.u8vector_elements(vector_data))
                
                # 3. Duplicate N times
                # Example: [A, B] * 3 -> [A, B, A, B, A, B]
                new_bytes = input_bytes * self.n
                
                # 4. Create new PMT
                out_vector = pmt.init_u8vector(len(new_bytes), new_bytes)
                out_msg = pmt.cons(meta, out_vector)
                
                # 5. Send
                self.message_port_pub(pmt.intern("pdu_out"), out_msg)
        except Exception as e:
            print(f"[Duplicator] Error: {e}")