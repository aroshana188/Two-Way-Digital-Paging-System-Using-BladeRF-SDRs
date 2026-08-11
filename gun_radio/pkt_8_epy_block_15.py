import numpy as np
from gnuradio import gr
import pmt
import time

class ack_decoder(gr.basic_block):
    def __init__(self, log_file=''):
        gr.basic_block.__init__(self,
            name="ACK Decoder",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)
        self.message_port_register_out(pmt.intern("rn_out"))
        
        self.log_file_path = log_file
        if self.log_file_path != '':
            try:
                with open(self.log_file_path, 'w') as f:
                    f.write("--- ACK DECODER LOG START ---\n")
            except: pass

    def log(self, msg):
        print(msg)
        if self.log_file_path != '':
            try:
                with open(self.log_file_path, 'a') as f:
                    t = time.strftime("%H:%M:%S", time.localtime())
                    f.write(f"[{t}] {msg}\n")
            except: pass

    def handle_msg(self, msg):
        try:
            payload_pmt = pmt.cdr(msg)
            data_list = pmt.u8vector_elements(payload_pmt)
            if len(data_list) < 3: return

            rn_val = data_list[-1]
            
            out_payload = [rn_val]
            out_vec = pmt.init_u8vector(1, out_payload)
            out_msg = pmt.cons(pmt.PMT_NIL, out_vec)
            
            self.message_port_pub(pmt.intern("rn_out"), out_msg)
            
            self.log(f"[ACK Decoder ACK]           Received Request for #{rn_val}")

        except Exception as e:
            self.log(f"[ACK Error] {e}")