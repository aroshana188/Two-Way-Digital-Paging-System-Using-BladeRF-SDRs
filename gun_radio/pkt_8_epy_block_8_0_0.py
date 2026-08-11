"""
Embedded Python Block: ACK Generator (No Preamble, IP + Type Support)
"""

import numpy as np
from gnuradio import gr
import pmt
import struct
import time
import socket

class ack_generator(gr.basic_block):
    def __init__(self, my_ip="192.168.1.20", payload_len=100, ack_interval=0.1):
        """
        Args:
            my_ip: The IP of THIS receiver.
            payload_len: Padding length.
            ack_interval: Throttling time for duplicate ACKs.
        """
        gr.basic_block.__init__(self,
            name="ACK Generator",
            in_sig=None,
            out_sig=None)

        self.p_len = payload_len
        self.interval = ack_interval
        
        # Constant: Type 1 = ACK
        self.MSG_TYPE_ACK = 1

        # Convert My IP to Bytes
        try:
            self.my_ip_bytes = socket.inet_aton(my_ip)
        except OSError:
            print(f"[ACK Gen] Error: Invalid IP {my_ip}")
            self.my_ip_bytes = b'\x00\x00\x00\x00'

        # State
        self.last_dest_ip = None
        self.last_rn = -1
        self.last_time = 0.0

        self.message_port_register_in(pmt.intern("msg_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        self.set_msg_handler(pmt.intern("msg_in"), self.handle_msg)

    def handle_msg(self, msg):
        if not pmt.is_pair(msg):
            return

        # Extract Target IP and Request Number
        target_ip_pmt = pmt.car(msg)
        req_num = pmt.to_long(pmt.cdr(msg))
        
        if pmt.is_u8vector(target_ip_pmt):
            target_ip_bytes = bytes(pmt.u8vector_elements(target_ip_pmt))
        else:
            return

        now = time.time()
        should_send = False

        # Throttling Logic
        if (target_ip_bytes == self.last_dest_ip) and (req_num == self.last_rn):
            if (now - self.last_time) >= self.interval:
                should_send = True
        else:
            should_send = True

        if should_send:
            self.last_dest_ip = target_ip_bytes
            self.last_rn = req_num
            self.last_time = now
            
            # --- Create Header ---
            # Format: [ Dest(4B) ] [ Src(4B) ] [ Type(1B) ] [ RN(1B) ]
            # We set Type to 1 (self.MSG_TYPE_ACK)
            header = struct.pack('!4s4sBB', target_ip_bytes, self.my_ip_bytes, self.MSG_TYPE_ACK, req_num)

            # --- Create Payload ---
            # Padding to keep transmitter on air (using 0x55 pattern)
            payload = b'\x55' * self.p_len
            
            # --- Combine (No Preamble) ---
            full_data = header + payload

            # --- Publish ---
            meta = pmt.make_dict()
            out_vector = pmt.init_u8vector(len(full_data), list(full_data))
            out_msg = pmt.cons(meta, out_vector)

            self.message_port_pub(pmt.intern("pdu_out"), out_msg)