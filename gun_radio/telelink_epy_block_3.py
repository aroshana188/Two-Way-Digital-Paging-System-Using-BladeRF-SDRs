import numpy as np
from gnuradio import gr
import pmt

class aes_decrypt_pdu(gr.basic_block):
    def __init__(self, key_str='1234567890123456'):
        gr.basic_block.__init__(self,
            name="AES Decrypt PDU (Header Aware)",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)
        self.message_port_register_out(pmt.intern("pdu_out"))

        # Robust Fix: Convert to string first to avoid GRC integer errors
        self.key = str(key_str).encode('utf-8')

    def handle_msg(self, msg):
        try:
            # LAZY IMPORT
            from Crypto.Cipher import AES
            from Crypto.Util import Counter

            payload_pmt = pmt.cdr(msg)
            data_list = pmt.u8vector_elements(payload_pmt)
            
            # Safety Check: Must have [SRC, DST, SEQ] + Data
            if len(data_list) < 3: return

            # --- HEADER PARSING (The Fix) ---
            # 1. Extract Headers (Keep them safe to send out later)
            src_addr = data_list[0]
            dst_addr = data_list[1]
            
            # 2. Extract Sequence Number (It is the 3rd byte, Index 2)
            seq_num = data_list[2]
            
            # 3. Extract Encrypted Data (Everything after the first 3 bytes)
            encrypted_data = bytes(data_list[3:])
            # ----------------------

            # 4. Setup Cipher (Must match Transmitter logic)
            # Use seq_num to sync the counter
            ctr = Counter.new(128, initial_value=seq_num + 1)
            cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
            
            # 5. Decrypt
            decrypted_bytes = cipher.decrypt(encrypted_data)
            
            # 6. Rebuild PDU: [SRC, DST, SEQ, Decrypted Data]
            # We include headers so your File Sink can strip them correctly
            out_list = [src_addr, dst_addr, seq_num] + list(decrypted_bytes)
            
            out_vec = pmt.init_u8vector(len(out_list), out_list)
            out_msg = pmt.cons(pmt.PMT_NIL, out_vec)
            
            self.message_port_pub(pmt.intern("pdu_out"), out_msg)

        except Exception as e:
            print(f"[AES Decrypt Error] {e}")