"""
Embedded Python Block: Selective AES Decryptor
Function:
1. Reads 12-Byte Cleartext Header.
2. Decrypts the Payload (Bytes 12+) using AES-128 ECB.
"""
import numpy as np
from gnuradio import gr
import pmt
from Crypto.Cipher import AES

class selective_aes_decrypt(gr.basic_block):
    def __init__(self, key_str="1234567890123456"):
        gr.basic_block.__init__(self,
            name="Selective AES Decryptor",
            in_sig=None,
            out_sig=None)

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
            
            # Header is 12 bytes
            if len(data) < 12:
                return

            # 1. Split Header and Encrypted Payload
            header = data[0:12]
            encrypted_payload = data[12:]
            
            # 2. Decrypt
            if len(encrypted_payload) > 0 and len(encrypted_payload) % 16 == 0:
                try:
                    cipher = AES.new(self.key, AES.MODE_ECB)
                    decrypted_bytes = cipher.decrypt(bytes(encrypted_payload))
                    
                    # 3. Recombine
                    final_packet = header + list(decrypted_bytes)
                    
                    # 4. Output
                    out_pdu = pmt.init_u8vector(len(final_packet), final_packet)
                    out_msg = pmt.cons(pmt.PMT_NIL, out_pdu)
                    self.message_port_pub(pmt.intern("out"), out_msg)
                    
                except ValueError:
                    print("[AES Decrypt] Decryption Failed (Key mismatch or corrupt data)")
            else:
                # If payload is empty or not aligned, pass it through (might be header only)
                # or drop it. Here we pass it safe.
                self.message_port_pub(pmt.intern("out"), msg)

        except Exception as e:
            print(f"[AES Decrypt] Error: {e}")