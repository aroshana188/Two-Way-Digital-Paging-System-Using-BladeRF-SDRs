"""
Embedded Python Block: PDU Splitter
"""

import numpy as np
from gnuradio import gr
import pmt

class pdu_splitter(gr.basic_block):
    def __init__(self, num_duplicates=10):
        # Default num_duplicates set to 10 to match your transmitter image
        gr.basic_block.__init__(self,
            name="PDU Splitter",
            in_sig=None,
            out_sig=None)
        
        self.n = num_duplicates

        # Register Ports
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        
        # Bind Handler
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        # Ensure we are handling a PDU
        if pmt.is_pdu(msg):
            meta = pmt.car(msg)
            vector_data = pmt.cdr(msg)
            
            # Convert PMT vector to Python list/tuple of bytes
            data = pmt.u8vector_elements(vector_data)
            total_len = len(data)
            
            # Validation: The total length must be divisible by N
            if total_len == 0 or (total_len % self.n != 0):
                # If the packet size is wrong (likely due to noise shifting the header),
                # we cannot safely split it. Drop it.
                return

            # Calculate the size of one sub-packet (Payload + CRC)
            chunk_len = total_len // self.n
            
            # Loop N times to slice and send each copy
            for i in range(self.n):
                start = i * chunk_len
                end = start + chunk_len
                
                # Extract the slice
                sub_packet = data[start:end]
                
                # Create new PMT vector
                out_vector = pmt.init_u8vector(len(sub_packet), sub_packet)
                
                # Create new PDU (preserving original metadata)
                out_msg = pmt.cons(meta, out_vector)
                
                # Send to output
                self.message_port_pub(pmt.intern("pdu_out"), out_msg)