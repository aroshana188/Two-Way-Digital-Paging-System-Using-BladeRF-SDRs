"""
Embedded Python Block: Priority PDU Mux (Strict Scheduler)
Function: Buffers and releases packets based on strict 4-level priority.
1. Emergency ACKs
2. Emergency Messages
3. Normal ACKs
4. Normal Messages
"""
import numpy as np
from gnuradio import gr
import pmt
import threading
import time

class priority_mux(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Priority PDU Mux",
            in_sig=None,
            out_sig=None)

        # 1. Register Inputs
        self.message_port_register_in(pmt.intern("data_in")) # From Storage
        self.message_port_register_in(pmt.intern("ack_in"))  # From ACK Gen
        
        # 2. Register Output
        self.message_port_register_out(pmt.intern("pdu_out"))

        # 3. Bind Handlers
        self.set_msg_handler(pmt.intern("data_in"), self.handle_pdu)
        self.set_msg_handler(pmt.intern("ack_in"), self.handle_pdu) # Use same handler for logic
        
        # 4. Internal Queues (Strict Priority)
        self.q1_ack_high = [] # Ack E
        self.q2_msg_high = [] # Msg E
        self.q3_ack_low  = [] # Ack N
        self.q4_msg_low  = [] # Msg N

        self.running = True
        self.lock = threading.Lock()

        # 5. Start Scheduler Thread
        self.worker = threading.Thread(target=self.process_loop, daemon=True)
        self.worker.start()

    def get_header_info(self, u8_list):
        """
        Reads Header:
        Byte 8  = Type ('M' or 'A')
        Byte 11 = Priority ('E' or 'N')
        """
        try:
            pkt_type = u8_list[8]
            prio_byte = u8_list[11]
            return pkt_type, prio_byte
        except IndexError:
            # Malformed packet, default to Normal Msg to flush it out
            return ord('M'), ord('N')

    def handle_pdu(self, msg):
        """
        Buffering Handler.
        Instead of sending immediately, we inspect and queue it.
        """
        with self.lock:
            payload = pmt.cdr(msg)
            
            # Convert to list to read bytes
            if pmt.is_u8vector(payload):
                u8_list = list(pmt.u8vector_elements(payload))
            else:
                return # Ignore invalid data

            pkt_type, prio_byte = self.get_header_info(u8_list)
            
            # --- SORTING LOGIC ---
            
            # 1. Emergency ACKs (Type=A, Prio=E)
            if pkt_type == ord('A') and prio_byte == ord('E'):
                self.q1_ack_high.append(u8_list)
                
            # 2. Emergency Msgs (Type=M, Prio=E)
            elif pkt_type == ord('M') and prio_byte == ord('E'):
                self.q2_msg_high.append(u8_list)
                
            # 3. Normal ACKs (Type=A, Prio!=E)
            elif pkt_type == ord('A'):
                self.q3_ack_low.append(u8_list)
                
            # 4. Normal Msgs (Type=M, Prio!=E)
            else:
                self.q4_msg_low.append(u8_list)

    def process_loop(self):
        """
        Active Scheduler Thread.
        Checks queues in strict 1 -> 4 order.
        """
        while self.running:
            packet_to_send = None
            
            with self.lock:
                # Strict Priority Check
                if len(self.q1_ack_high) > 0:
                    packet_to_send = self.q1_ack_high.pop(0)
                    # Optional: print("[Mux] Sending Priority 1: Emergency ACK")
                    
                elif len(self.q2_msg_high) > 0:
                    packet_to_send = self.q2_msg_high.pop(0)
                    # Optional: print("[Mux] Sending Priority 2: Emergency Msg")
                    
                elif len(self.q3_ack_low) > 0:
                    packet_to_send = self.q3_ack_low.pop(0)
                    # Optional: print("[Mux] Sending Priority 3: Normal ACK")
                    
                elif len(self.q4_msg_low) > 0:
                    packet_to_send = self.q4_msg_low.pop(0)
                    # Optional: print("[Mux] Sending Priority 4: Normal Msg")

            if packet_to_send:
                # Construct PMT and Send
                out_pmt = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(packet_to_send), packet_to_send))
                self.message_port_pub(pmt.intern("pdu_out"), out_pmt)
                
                # Small delay to prevent bus saturation
                time.sleep(0.001) 
            else:
                # Idle sleep to save CPU
                time.sleep(0.01)