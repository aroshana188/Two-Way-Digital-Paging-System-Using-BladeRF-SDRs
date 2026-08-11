import numpy as np
from gnuradio import gr
import pmt
import time

class sequence_checker(gr.basic_block):
    def __init__(self, initial_rn=0, log_file=''):
        gr.basic_block.__init__(self,
            name="Sequence Check",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)
        self.message_port_register_out(pmt.intern("frame_out"))
        self.message_port_register_out(pmt.intern("rn_out"))

        self.current_rn = initial_rn
        self.log_file_path = log_file
        
        # Init Log
        if self.log_file_path != '':
            try:
                with open(self.log_file_path, 'w') as f:
                    f.write("--- COMMUNICATION START ---\n")
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

            incoming_src = data_list[0]
            incoming_dst = data_list[1]
            incoming_sn  = data_list[2]

            # --- SKIP LOGIC START ---
            
            # Calculate the "Distance" forward. 
            diff = (incoming_sn - self.current_rn + 256) % 256
            
            if diff == 0:
                # EXACT MATCH
                self.message_port_pub(pmt.intern("frame_out"), msg)
                self.current_rn = (self.current_rn + 1) % 256
                self.log(f"[Sqnc Checker Match]        Got #{incoming_sn}. Next: #{self.current_rn}")
                
            elif diff < 10: 
                # SMALL SKIP DETECTED (e.g., missed 1 or 2 packets)
                self.log(f"[Sqnc Checker Skip]         Wanted #{self.current_rn}, but got #{incoming_sn}. Jumping forward.")
                
                # Output the packet we just got
                self.message_port_pub(pmt.intern("frame_out"), msg)
                
                # Update expectation to the ONE AFTER this new packet
                self.current_rn = (incoming_sn + 1) % 256
                
            else:
                # LARGE GAP or OLD PACKET
                self.log(f"[Sqnc Checker Drop]         Got #{incoming_sn} (Expected #{self.current_rn}). Ignoring.")

            # ALWAYS send ACK for what we want NEXT
            self.send_ack_packet(incoming_src, incoming_dst, self.current_rn)

        except Exception as e:
            self.log(f"[Sqnc Checker Error] {e}")

    def send_ack_packet(self, target_dst, my_src, rn_val):
        try:
            ack_payload = [target_dst, my_src, rn_val]
            out_vec = pmt.init_u8vector(len(ack_payload), ack_payload)
            out_msg = pmt.cons(pmt.PMT_NIL, out_vec)
            self.message_port_pub(pmt.intern("rn_out"), out_msg)
        except Exception as e:
            self.log(f"[Sqnc Checker ACK Error] {e}")