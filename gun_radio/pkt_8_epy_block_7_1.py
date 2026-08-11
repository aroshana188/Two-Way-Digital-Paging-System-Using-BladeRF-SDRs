"""
Embedded Python Block: Address & Type Filter (IP Support)
"""

import numpy as np
from gnuradio import gr
import pmt
import socket

class addr_type_filter(gr.basic_block):
    def __init__(self, my_ip="192.168.1.20"):
        """
        Args:
            my_ip: The IP address of THIS receiver (String).
        """
        gr.basic_block.__init__(self,
            name="Address & Type Filter",
            in_sig=None,
            out_sig=None)

        self.my_ip_str = my_ip
        
        # Convert IP string to 4-byte binary
        try:
            self.my_ip_bytes = list(socket.inet_aton(self.my_ip_str))
        except OSError:
            print(f"[Error] Invalid IP format: {my_ip}")
            self.my_ip_bytes = [0, 0, 0, 0]

        # Register Ports
        self.message_port_register_in(pmt.intern("pdu_in"))
        
        # Output 1: Data PDUs (Goes to Sequence Checker)
        self.message_port_register_out(pmt.intern("data_out"))
        
        # Output 2: ACK Integers (Goes DIRECTLY to PDU Storage 'request_in')
        self.message_port_register_out(pmt.intern("ack_out"))
        
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        # 1. Validate Input
        if not pmt.is_pdu(msg):
            return

        data_pdu = pmt.cdr(msg)
        data_bytes = list(pmt.u8vector_elements(data_pdu))

        # 2. Safety Check
        # Header: [Dest 4B] [Src 4B] [Type 1B] [Seq/RN 1B] ...
        # We need at least 10 bytes to process a valid packet
        if len(data_bytes) < 10:
            return

        # 3. Check Destination (Bytes 0-3)
        dest_received = data_bytes[0:4]
        
        if dest_received != self.my_ip_bytes:
            # Not for us -> Drop it
            return

        # 4. Extract Header Info
        src_received = data_bytes[4:8]
        pkt_type     = data_bytes[8]
        seq_or_rn    = data_bytes[9]

        # 5. Logic Branch
        if pkt_type == 0:
            # === CASE: DATA MESSAGE ===
            # We need to send [Seq Num] [Payload] to the Sequence Checker.
            # We strip the first 9 bytes (Dest, Src, Type).
            # We KEEP the Seq Num (Byte 9) because Sequence Checker needs it.
            clean_payload = data_bytes[9:] 
            
            # Save Source IP to Metadata (Required for replying with ACK)
            meta = pmt.car(msg)
            src_ip_pmt = pmt.init_u8vector(4, src_received)
            meta = pmt.dict_add(meta, pmt.intern("src_ip"), src_ip_pmt)
            
            # Create PDU
            out_vector = pmt.init_u8vector(len(clean_payload), clean_payload)
            out_msg = pmt.cons(meta, out_vector)
            
            # Send to Sequence Checker
            self.message_port_pub(pmt.intern("data_out"), out_msg)

        elif pkt_type == 1:
            # === CASE: ACKNOWLEDGMENT ===
            # The 'seq_or_rn' byte IS the Request Number we need.
            # We don't need a PDU here; PDU Storage expects a simple Integer.
            
            # Create PMT Integer
            ack_msg = pmt.from_long(seq_or_rn)
            
            # Send to PDU Storage (request_in)
            self.message_port_pub(pmt.intern("ack_out"), ack_msg)
            # print(f"[RX Filter] Received ACK {seq_or_rn} from {src_received}")