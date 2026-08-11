import numpy as np
from gnuradio import gr
import pmt
import time

class crc_fail_logger(gr.basic_block):
    def __init__(self, log_file=''):
        gr.basic_block.__init__(self,
            name="CRC Fail Logger",
            in_sig=None,
            out_sig=None)

        # INPUT: Connect this to the 'fail' port of the CRC Check block
        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)
        
        self.fail_count = 0
        
        # LOGGING SETUP
        self.log_file_path = log_file
        if self.log_file_path != '':
            try:
                with open(self.log_file_path, 'w') as f:
                    f.write("--- CRC FAILURE LOG START ---\n")
            except: pass

    def log(self, message):
        """Helper function to Print AND Write to file"""
        print(message)
        if self.log_file_path != '':
            try:
                with open(self.log_file_path, 'a') as f:
                    timestamp = time.strftime("%H:%M:%S", time.localtime())
                    f.write(f"[{timestamp}] {message}\n")
            except: pass

    def handle_msg(self, msg):
        try:
            self.fail_count += 1
            
            # Extract the length of the bad packet just for info
            payload = pmt.cdr(msg)
            data_len = len(pmt.u8vector_elements(payload))
            
            self.log(f"[CRC FAIL] Corrupted Packet Dropped! (Size: {data_len} bytes | Total Fails: {self.fail_count})")
            
        except Exception as e:
            self.log(f"[CRC Log Error] {e}")