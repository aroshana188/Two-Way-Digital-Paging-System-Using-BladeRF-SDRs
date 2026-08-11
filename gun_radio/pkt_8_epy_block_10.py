"""
Embedded Python Block: PDU Splitter
Function: Splits a large PDU into N smaller PDUs and sends them sequentially.
"""
import numpy as np
from gnuradio import gr
import pmt

class pdu_splitter(gr.basic_block):
    def __init__(self, num_duplicates=3):
        # NOTE: Make sure this matches your Transmitter's num_duplicates!
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
        try:
            if pmt.is_pdu(msg):
                meta = pmt.car(msg)
                vector_data = pmt.cdr(msg)
                
                # Get Data
                data = list(pmt.u8vector_elements(vector_data))
                total_len = len(data)
                
                # --- VALIDATION ---
                # The total length must be exactly divisible by N.
                # If not, the packet header length tag was likely corrupted by noise.
                if total_len == 0:
                    return
                
                if total_len % self.n != 0:
                    # print(f"[Splitter] Dropping malformed packet. Length {total_len} not divisible by {self.n}")
                    return

                # Calculate single packet size
                chunk_len = total_len // self.n
                
                # --- SPLIT & SEND LOOP ---
                for i in range(self.n):
                    start = i * chunk_len
                    end = start + chunk_len
                    
                    # Slice the data
                    sub_packet = data[start:end]
                    
                    # Create PDU
                    out_vector = pmt.init_u8vector(len(sub_packet), sub_packet)
                    out_msg = pmt.cons(meta, out_vector)
                    
                    # Publish
                    self.message_port_pub(pmt.intern("pdu_out"), out_msg)
                    
        except Exception as e:
            print(f"[Splitter] Error: {e}")