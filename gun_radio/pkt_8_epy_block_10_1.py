import numpy as np
from gnuradio import gr
import pmt

class dest_addr_check(gr.basic_block):
    def __init__(self, my_address=20):
        gr.basic_block.__init__(self,
            name="Destination Address Filter",
            in_sig=None,
            out_sig=None)

        # 1. Register Input (From CRC Block)
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

        # 2. Register Output (To ARQ/Decoder Block)
        self.message_port_register_out(pmt.intern("pdu_out"))

        # 3. Store My Address
        self.my_addr = my_address

    def handle_msg(self, msg):
        try:
            # Extract data from PDU
            payload_pmt = pmt.cdr(msg)
            data_list = pmt.u8vector_elements(payload_pmt)
            
            # Safety Check: Packet must be at least 2 bytes (SRC + DST)
            if len(data_list) < 2:
                return

            # --- ADDRESS LOGIC ---
            # Based on your structure: Byte 0 = SRC, Byte 1 = DST
            packet_dst = data_list[1] 

            # Compare
            if packet_dst == self.my_addr:
                # MATCH: Valid packet for me.
                # Pass the WHOLE frame (header + payload) to the next block.
                self.message_port_pub(pmt.intern("pdu_out"), msg)
            else:
                # MISMATCH: Packet is for someone else.
                # Drop it silently (or print for debug)
                # print(f"Dropped packet for User #{packet_dst}")
                pass

        except Exception as e:
            print(f"[Addr Check Error] {e}")