import numpy as np
from gnuradio import gr
import pmt
import os

class pdu_file_sink(gr.basic_block):
    def __init__(self, file_path='/home/user/output.txt', append_to_file=False):
        gr.basic_block.__init__(self,
            name="PDU to Text File Sink",
            in_sig=None,
            out_sig=None)

        # INPUT: Validated Frames from Sequence Checker
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

        self.file_path = file_path
        
        # Logic to handle file modes
        # If append is False, we delete the old file when the flowgraph starts
        if not append_to_file:
            if os.path.exists(self.file_path):
                try:
                    os.remove(self.file_path)
                    print(f"[File Sink] Deleted old file: {self.file_path}")
                except Exception as e:
                    print(f"[File Sink Error] Could not clean file: {e}")

    def handle_msg(self, msg):
        try:
            # 1. Extract Data
            payload_pmt = pmt.cdr(msg)
            data_list = pmt.u8vector_elements(payload_pmt)
            
            # Safety Check: Must have at least 3 bytes header + 1 byte data
            if len(data_list) < 4:
                return

            # 2. Strip Header (SRC, DST, SN)
            # The actual text starts at index 3
            raw_payload = bytes(data_list[3:])
            
            # 3. Remove Zero Padding
            # This removes any 0x00 bytes from the RIGHT side of the packet
            clean_payload = raw_payload.rstrip(b'\x00')
            
            # 4. Decode to Text
            # We use 'replace' to prevent crashing if a bit error slipped through
            text_data = clean_payload.decode('utf-8', errors='replace')
            
            # 5. Write to File
            # We open in 'a' (append) mode so we add to the end of the file
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(text_data)
                # Note: We do NOT add a newline here, because the original file 
                # might have been split in the middle of a sentence.
                
            # Optional: Print progress
            # print(f"[File Sink] Wrote {len(text_data)} characters.")

        except Exception as e:
            print(f"[File Sink Error] {e}")