"""
Embedded Python Block: AES Decrypt
"""

import numpy as np
from gnuradio import gr
import pmt
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class aes_decrypt_pdu(gr.basic_block):
    def __init__(self, key_str="1234567890123456"):
        """
        Args:
            key_str: Must match the Transmitter's key!
        """
        gr.basic_block.__init__(self,
            name="AES Decrypt PDU",
            in_sig=None,
            out_sig=None)

        self.key = key_str.encode('utf-8')[:16].ljust(16, b'\0')
        self.iv = b'\x00' * 16

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        if not pmt.is_pdu(msg):
            return

        meta = pmt.car(msg)
        data_pdu = pmt.cdr(msg)
        encrypted_bytes = bytes(pmt.u8vector_elements(data_pdu))
        
        if len(encrypted_bytes) == 0:
            return

        # 1. Decrypt
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)

        try:
            # 2. Decrypt and Unpad
            decrypted_payload = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
            
            # 3. Publish clean data
            out_vector = pmt.init_u8vector(len(decrypted_payload), list(decrypted_payload))
            out_msg = pmt.cons(meta, out_vector)
            self.message_port_pub(pmt.intern("pdu_out"), out_msg)
            
        except ValueError:
            # This happens if decryption fails (e.g. padding error due to corruption)
            print("[AES Decrypt] Error: Padding incorrect (Packet corrupted?)")
        except Exception as e:
            print(f"[AES Decrypt] Error: {e}")