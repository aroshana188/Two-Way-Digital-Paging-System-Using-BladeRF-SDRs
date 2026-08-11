"""
Embedded Python Block: PDU File Sink (With Append Option)
"""

import numpy as np
from gnuradio import gr
import pmt
import os

class pdu_file_sink(gr.basic_block):
    def __init__(self, filename="received_output.txt", append=False):
        gr.basic_block.__init__(self,
            name="PDU File Sink",
            in_sig=None,
            out_sig=None)

        self.filename = filename
        self.append = append
        self.file_handle = None

        # Register Input Port
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

        # Determine Mode: 'ab' = Append Binary, 'wb' = Write Binary (Overwrite)
        mode = 'ab' if self.append else 'wb'

        try:
            self.file_handle = open(self.filename, mode)
            action = "Appending to" if self.append else "Overwriting"
            print(f"PDU File Sink: {action} {self.filename}")
        except Exception as e:
            print(f"PDU File Sink Error: Could not open file. {e}")

    def handle_msg(self, msg):
        # 1. Validate PDU
        if not pmt.is_pdu(msg):
            return

        # 2. Extract Data
        data_vector = pmt.cdr(msg)
        
        # 3. Convert to Bytes
        data_bytes = bytearray(pmt.u8vector_elements(data_vector))
        
        # 4. Write to Disk
        if self.file_handle:
            self.file_handle.write(data_bytes)
            self.file_handle.flush() # Force save immediately

    def __del__(self):
        if self.file_handle:
            self.file_handle.close()