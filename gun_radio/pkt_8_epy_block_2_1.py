"""
Embedded Python Block: AES Encrypt (Preserve SN)
"""

import numpy as np
from gnuradio import gr
import pmt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class aes_encrypt_pdu(gr.basic_block):
    def __init__(self, key_str="1234567890123456"):
        """
        Args:
            key_str: 16-byte encryption key (String)
        """
        gr.basic_block.__init__(self,
            name="AES Encrypt PDU",
            in_sig=None,
            out_sig=None)

        # Ensure key is 16 bytes (AES-128)
        self.key = key_str.encode('utf-8')[:16].ljust(16, b'\0')
        # Fixed IV for simplicity (In production, use random IV and send it)
        self.iv = b'\x00' * 16

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        if not pmt.is_pdu(msg):
            return

        meta = pmt.car(msg)
        data_pdu = pmt.cdr(msg)
        data_bytes = bytearray(pmt.u8vector_elements(data_pdu))

        if len(data_bytes) < 1:
            return

        # 1. Separate SN and Payload
        sn_byte = data_bytes[0:1]       # First byte is Sequence Number
        payload = data_bytes[1:]        # Rest is Data

        # 2. Encrypt Payload
        # We must create a new Cipher for every packet to reset state
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        
        try:
            # Pad payload to be a multiple of 16 bytes
            encrypted_payload = cipher.encrypt(pad(payload, AES.block_size))
            
            # 3. Reassemble: [SN] [Encrypted Payload]
            new_data = sn_byte + encrypted_payload

            # 4. Publish
            out_vector = pmt.init_u8vector(len(new_data), list(new_data))
            out_msg = pmt.cons(meta, out_vector)
            self.message_port_pub(pmt.intern("pdu_out"), out_msg)
            
        except Exception as e:
            print(f"[AES Encrypt] Error: {e}")