"""
Embedded Python Block: CRC Fail Logger (With Counter)
Function: 
1. Counts total CRC failures.
2. Prints warning + count + packet length to console.
"""
import numpy as np
from gnuradio import gr
import pmt
import datetime

class crc_fail_logger(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="CRC Fail Logger",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)
        
        # Initialize Counter
        self.fail_count = 0

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def handle_msg(self, msg):
        try:
            # Increment Counter
            self.fail_count += 1
            timestamp = self.get_timestamp()
            
            # Check length to distinguish noise from partial packets
            payload = pmt.cdr(msg)
            length_str = "?"
            if pmt.is_u8vector(payload):
                length = len(pmt.u8vector_elements(payload))
                length_str = str(length)

            # Print Detailed Log
            print(f"[{timestamp}] [CRC FAIL] Corrupted packet received (Length: {length_str} bytes). Discarding. #{self.fail_count}")
                
        except Exception as e:
            print(f"[CRC Logger] Error: {e}")