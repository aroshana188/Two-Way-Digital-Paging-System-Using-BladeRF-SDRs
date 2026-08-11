"""
Embedded Python Block: PDU Duplicator
"""

import numpy as np
from gnuradio import gr
import pmt

class pdu_duplicator(gr.basic_block):
    def __init__(self, num_duplicates=3):
        # Default value ensures GRC doesn't throw an error
        gr.basic_block.__init__(self,
            name="PDU Duplicator",
            in_sig=None,
            out_sig=None)
        
        # Save parameter
        self.n = num_duplicates

        # Register Ports
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        
        # Bind Handler
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        # 1. Check if the message is a valid PDU
        if pmt.is_pdu(msg):
            # Extract metadata and data vector
            meta = pmt.car(msg)
            vector_data = pmt.cdr(msg)
            
            # 2. Convert PMT vector to a standard Python list of bytes
            # The input 'vector_data' already contains [Payload + CRC]
            input_bytes = pmt.u8vector_elements(vector_data)
            
            # 3. Duplicate the list N times
            # In Python, [1, 2] * 3 becomes [1, 2, 1, 2, 1, 2]
            new_bytes = list(input_bytes) * self.n
            
            # 4. Create a new PMT u8vector from the long list
            out_vector = pmt.init_u8vector(len(new_bytes), new_bytes)
            
            # 5. Create the new PDU (preserving original metadata)
            out_msg = pmt.cons(meta, out_vector)
            
            # 6. Publish
            self.message_port_pub(pmt.intern("pdu_out"), out_msg)