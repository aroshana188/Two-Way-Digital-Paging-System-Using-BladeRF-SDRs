"""
Embedded Python Block: ACK Generator
Input:  [Dest=Me | Src=Sender | Type=? | MsgID | RN | Prio | Padding(00...)]
Output: [Dest=Sender | Src=Me | Type='A' | MsgID | RN | Prio | Dummy(AA...)]
"""
import numpy as np
from gnuradio import gr
import pmt

class ack_generator(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="ACK Generator",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            payload = pmt.cdr(msg)
            if not pmt.is_u8vector(payload): return
            
            # Convert to mutable list
            data = list(pmt.u8vector_elements(payload))
            if len(data) < 12: return

            # --- 1. SWAP ADDRESSES (Bounce Back) ---
            me_ip = data[0:4] 
            sender_ip = data[4:8] 

            data[0:4] = sender_ip 
            data[4:8] = me_ip 

            # --- 2. SET PACKET TYPE TO 'A' (ACK) ---
            data[8] = ord('A')

            # --- 3. FILL PAYLOAD WITH DUMMY DATA (0xAA) ---
            # Everything after the 12-byte header is payload
            # 0xAA = 10101010 (Good for keeping bit sync active)
            for i in range(12, len(data)):
                data[i] = 0xAA

            # --- 4. OUTPUT ---
            out_pdu = pmt.init_u8vector(len(data), data)
            out_msg = pmt.cons(pmt.PMT_NIL, out_pdu)
            self.message_port_pub(pmt.intern("pdu_out"), out_msg)

        except Exception as e:
            print(f"[ACK Gen] Error: {e}")