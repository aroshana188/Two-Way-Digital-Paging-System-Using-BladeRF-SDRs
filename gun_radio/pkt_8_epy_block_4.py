"""
Embedded Python Block: Advanced Packetizer (Fragmentation & Priority & Delay)
Packet Structure (12B Header + Payload):
[Dst(4) | Src(4) | PktType(1) | MsgID(1) | SeqNum(1) | Prio(1) | Payload(N)]
"""
import numpy as np
from gnuradio import gr
import pmt
import struct
import math
import time

class AdvancedPacketizer(gr.basic_block):
    def __init__(self, payload_len=48, delay=0.05):
        gr.basic_block.__init__(self,
            name="Advanced Packetizer",
            in_sig=None,
            out_sig=None)
        
        self.payload_len = payload_len
        self.delay = delay      # Delay in seconds
        self.msg_id_counter = 0 
        
        # Protocol Constants
        self.TYPE_MSG = ord('M') 
        self.SEQ_EOM  = 99       

        self.message_port_register_in(pmt.intern("in"))
        self.message_port_register_out(pmt.intern("out"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)

    def parse_ip(self, ip_str):
        try:
            return [int(x) for x in ip_str.strip().split('.')]
        except:
            return [0, 0, 0, 0]

    def handle_msg(self, msg):
        try:
            payload_pmt = pmt.cdr(msg)
            if pmt.is_symbol(payload_pmt):
                full_text = pmt.symbol_to_string(payload_pmt)
            elif pmt.is_u8vector(payload_pmt):
                u8_list = pmt.u8vector_elements(payload_pmt)
                full_text = "".join([chr(x) for x in u8_list])
            else:
                full_text = str(payload_pmt)
        except Exception as e:
            print(f"[Packetizer] Input Error: {e}")
            return

        try:
            if " >> " not in full_text:
                return
                
            meta_part, msg_content = full_text.split(" >> ", 1)
            
            src_str = meta_part.split("SRC:")[1].split(" ")[0]
            src_bytes = self.parse_ip(src_str)
            
            dst_str = meta_part.split("IP:")[1].split(" ")[0]
            dst_bytes = self.parse_ip(dst_str)
            
            if "MSG:[E]" in meta_part:
                prio_byte = ord('E')
            else:
                prio_byte = ord('N')

        except Exception as e:
            print(f"[Packetizer] Parsing Logic Error: {e}")
            return

        # --- FRAGMENTATION ---
        full_payload_bytes = [ord(c) for c in msg_content]
        total_len = len(full_payload_bytes)
        
        if total_len == 0:
            num_chunks = 1
        else:
            num_chunks = math.ceil(total_len / self.payload_len)

        if num_chunks > 98:
            num_chunks = 98

        # --- LOOP THROUGH CHUNKS ---
        for i in range(num_chunks):
            start = i * self.payload_len
            end = start + self.payload_len
            chunk_data = full_payload_bytes[start:end]
            
            current_len = len(chunk_data)
            if current_len < self.payload_len:
                padding = [0] * (self.payload_len - current_len)
                chunk_data = chunk_data + padding
            
            # Header Construction
            header = []
            header.extend(dst_bytes)            # Dst Addr
            header.extend(src_bytes)            # Src Addr
            header.append(self.TYPE_MSG)        # Type
            header.append(self.msg_id_counter)  # Msg ID
            header.append(i)                    # Seq Num
            header.append(prio_byte)            # Priority
            
            final_packet = header + chunk_data
            
            self.send_pdu(final_packet)
            
            # Time Delay
            time.sleep(self.delay) 

        # --- SEND EOM PACKET ---
        eom_header = []
        eom_header.extend(dst_bytes)
        eom_header.extend(src_bytes)
        eom_header.append(self.TYPE_MSG)
        eom_header.append(self.msg_id_counter)
        eom_header.append(self.SEQ_EOM)         # Seq Num 99
        eom_header.append(prio_byte)
        
        # --- NEW: Fill payload with 99s ---
        eom_payload = [99] * self.payload_len
        eom_packet = eom_header + eom_payload
        
        self.send_pdu(eom_packet)
        
        print(f"[Packetizer] Sent MsgID {self.msg_id_counter} in {num_chunks} chunks.")
        self.msg_id_counter = (self.msg_id_counter + 1) % 256

    def send_pdu(self, packet_list):
        out_pmt = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(packet_list), packet_list))
        self.message_port_pub(pmt.intern("out"), out_pmt)