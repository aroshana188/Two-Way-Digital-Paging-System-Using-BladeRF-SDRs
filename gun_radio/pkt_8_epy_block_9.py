"""
Embedded Python Block: Selective AES Encryptor
Function: 
1. Reads 12-Byte Cleartext Header.
2. Encrypts the Payload (Bytes 12+) using AES-128 ECB.
"""
import numpy as np
from gnuradio import gr
import pmt
from Crypto.Cipher import AES

class selective_aes_encrypt(gr.basic_block):
    def __init__(self, key_str="1234567890123456"):
        gr.basic_block.__init__(self,
            name="Selective AES Encryptor",
            in_sig=None,
            out_sig=None)

        # Ensure key is 16 bytes
        self.key = key_str.encode('utf-8')[:16]
        while len(self.key) < 16:
            self.key += b'\0'

        self.message_port_register_in(pmt.intern("in"))
        self.message_port_register_out(pmt.intern("out"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            payload_pmt = pmt.cdr(msg)
            data = list(pmt.u8vector_elements(payload_pmt))
            
            # Safety Check: Header(12) + Min Block(16)
            if len(data) < 12:
                return

            # 1. Split Header and Payload
            header = data[0:12]      # Cleartext Header
            raw_payload = data[12:]  # To Be Encrypted
            
            # 2. Check Padding (AES requires multiple of 16)
            # The Advanced Packetizer *should* have done this, but we double-check.
            remainder = len(raw_payload) % 16
            if remainder != 0:
                pad_len = 16 - remainder
                raw_payload += [0] * pad_len
            
            # 3. Encrypt
            cipher = AES.new(self.key, AES.MODE_ECB)
            encrypted_bytes = cipher.encrypt(bytes(raw_payload))
            
            # 4. Recombine
            final_packet = header + list(encrypted_bytes)
            
            # 5. Output
            out_pdu = pmt.init_u8vector(len(final_packet), final_packet)
            out_msg = pmt.cons(pmt.PMT_NIL, out_pdu)
            self.message_port_pub(pmt.intern("out"), out_msg)

        except Exception as e:
            print(f"[AES Encrypt] Error: {e}")