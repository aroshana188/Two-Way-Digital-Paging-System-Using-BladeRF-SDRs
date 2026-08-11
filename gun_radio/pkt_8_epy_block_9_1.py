import numpy as np
from gnuradio import gr
import pmt

class add_src_dst(gr.basic_block):
    def __init__(self, src_addr=10, dst_addr=20):
        gr.basic_block.__init__(self,
            name="Add SRC/DST Addresses",
            in_sig=None,
            out_sig=None)

        # Input Port (From Storage Buffer)
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

        # Output Port (To CRC or Protocol Formatter)
        self.message_port_register_out(pmt.intern("pdu_out"))

        # Store addresses (Ensure they are between 0-255)
        self.src = src_addr
        self.dst = dst_addr

    def handle_msg(self, msg):
        try:
            # 1. Extract the existing PDU data (Seq Num + Payload)
            # msg is a pair: (metadata, data_vector)
            payload_pmt = pmt.cdr(msg)
            payload_list = pmt.u8vector_elements(payload_pmt)
            
            # 2. Create the New Header
            # We prepend the addresses to the existing data
            # Structure becomes: [SRC] [DST] [SEQ] [DATA...]
            header_bytes = [self.src, self.dst]
            
            # Combine them
            new_payload = header_bytes + list(payload_list)
            
            # 3. Repack into a PMT PDU
            new_vec = pmt.init_u8vector(len(new_payload), new_payload)
            new_msg = pmt.cons(pmt.PMT_NIL, new_vec)
            
            # 4. Send to next block
            self.message_port_pub(pmt.intern("pdu_out"), new_msg)
            
        except Exception as e:
            print(f"[Address Adder Error] {e}")