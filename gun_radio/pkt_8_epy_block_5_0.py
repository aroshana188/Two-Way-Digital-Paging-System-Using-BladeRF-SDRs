"""
Embedded Python Block: PDU Queue & Storage (Burst ARQ)
Logic: 
1. Priority Queues (Emergency > Requests > Normal)
2. Burst Send: Transmit Packet N times (Timeout interval).
3. Storage Loop: Iterate stored packets and Burst Send them repeatedly.
"""
import numpy as np
from gnuradio import gr
import pmt
import time
import threading

class PDUQueueStorage(gr.basic_block):
    def __init__(self, timeout=1.0, max_retries=5):
        """
        timeout: Delay between retransmissions in a burst.
        max_retries: Number of times to send in one burst (e.g., 5 -> A,A,A,A,A).
        """
        gr.basic_block.__init__(self,
            name="PDU Queue & Storage",
            in_sig=None,
            out_sig=None)

        self.timeout = timeout
        self.max_retries = max_retries
        self.running = True

        # --- QUEUES ---
        self.queue_emergency = []  # 1. New Emergency
        self.req_emergency = []    # 2. Emergency Requests
        self.req_normal = []       # 3. Normal Requests
        self.queue_normal = []     # 4. New Normal
        self.storage = []          # 5. Persistent Storage
        
        self.lock = threading.Lock()

        self.message_port_register_in(pmt.intern("pdu_in"))
        self.message_port_register_in(pmt.intern("rn_in"))
        self.message_port_register_out(pmt.intern("pdu_out"))
        
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_pdu)
        self.set_msg_handler(pmt.intern("rn_in"), self.handle_rn)

        self.worker_thread = threading.Thread(target=self.process_loop, daemon=True)
        self.worker_thread.start()

    def get_header_info(self, u8_list):
        try:
            # Header: [Dst(4)|Src(4)|Type(1)|MsgID(1)|Seq(1)|Prio(1)]
            msg_id = u8_list[9]
            seq_num = u8_list[10]
            prio_byte = u8_list[11]
            return msg_id, seq_num, prio_byte
        except:
            return 0, 0, 0

    def handle_pdu(self, msg):
        """Handle Incoming New Packet"""
        with self.lock:
            payload = pmt.cdr(msg)
            u8_list = list(pmt.u8vector_elements(payload))
            _, _, prio_byte = self.get_header_info(u8_list)
            
            if prio_byte == ord('E'):
                self.queue_emergency.append(u8_list)
            else:
                self.queue_normal.append(u8_list)

    def handle_rn(self, msg):
        """Handle Retransmission Request (ACK/NACK)"""
        with self.lock:
            try:
                payload = pmt.cdr(msg)
                rn_data = list(pmt.u8vector_elements(payload))
                req_msg_id = rn_data[0]
                req_seq_num = rn_data[1]
                
                # 1. Cumulative ACK: Delete all packets with Same MsgID but LOWER SeqNum
                # (Assuming they were received successfully)
                self.storage = [p for p in self.storage if not (p['msg_id'] == req_msg_id and p['seq'] < req_seq_num)]
                
                # 2. Specific Request: Find target and queue for Priority Burst
                for item in self.storage:
                    if item['msg_id'] == req_msg_id and item['seq'] == req_seq_num:
                        pdu_copy = list(item['pdu'])
                        if item['prio'] == ord('E'):
                            self.req_emergency.append(pdu_copy)
                        else:
                            self.req_normal.append(pdu_copy)
                        break 
            except Exception as e:
                print(f"[Queue] RN Error: {e}")

    def send_pdu_burst(self, pdu_list, is_new=False):
        """Helper to send a packet 'max_retries' times"""
        
        # If it's a NEW packet, we must add it to storage first
        # so it doesn't get lost if we crash or move on.
        if is_new:
            with self.lock:
                msg_id, seq_num, prio = self.get_header_info(pdu_list)
                # Check duplicate
                exists = any(p['msg_id'] == msg_id and p['seq'] == seq_num for p in self.storage)
                if not exists:
                    self.storage.append({
                        'pdu': pdu_list,
                        'msg_id': msg_id,
                        'seq': seq_num,
                        'prio': prio
                    })

        # --- BURST TRANSMISSION (A, A, A, A, A...) ---
        for i in range(self.max_retries):
            # Check for High Priority Interrupts
            if self.check_priority_interrupt(current_pdu=pdu_list):
                return # Stop this burst to handle Emergency

            # Check if Packet was ACKed (Removed from storage) mid-burst
            # (Only relevant if we are retransmitting from storage)
            if not is_new:
                with self.lock:
                    msg_id, seq_num, _ = self.get_header_info(pdu_list)
                    still_exists = any(p['msg_id'] == msg_id and p['seq'] == seq_num for p in self.storage)
                    if not still_exists:
                        return # Stop burst, it was ACKed!

            # Send
            out_pmt = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(pdu_list), pdu_list))
            self.message_port_pub(pmt.intern("pdu_out"), out_pmt)
            
            # Wait
            time.sleep(self.timeout)

    def check_priority_interrupt(self, current_pdu):
        """Returns True if a higher priority packet arrived"""
        # If we are sending Normal, check for Emergency
        _, _, prio = self.get_header_info(current_pdu)
        if prio == ord('N'):
            with self.lock:
                if len(self.queue_emergency) > 0 or len(self.req_emergency) > 0:
                    return True
        return False

    def process_loop(self):
        while self.running:
            target_pdu = None
            is_new = False
            
            # --- 1. CHECK QUEUES (Highest to Lowest) ---
            with self.lock:
                if len(self.queue_emergency) > 0:
                    target_pdu = self.queue_emergency.pop(0)
                    is_new = True
                elif len(self.req_emergency) > 0:
                    target_pdu = self.req_emergency.pop(0)
                    is_new = False
                elif len(self.req_normal) > 0:
                    target_pdu = self.req_normal.pop(0)
                    is_new = False
                elif len(self.queue_normal) > 0:
                    target_pdu = self.queue_normal.pop(0)
                    is_new = True
            
            if target_pdu:
                self.send_pdu_burst(target_pdu, is_new)
                continue # Loop back to check queues again
            
            # --- 2. STORAGE LOOP (Round Robin) ---
            # If Queues are empty, iterate through storage
            # We copy the list to avoid modification issues during iteration
            with self.lock:
                storage_snapshot = list(self.storage)
            
            if len(storage_snapshot) == 0:
                time.sleep(0.1) # Nothing to do
                continue

            for item in storage_snapshot:
                # Before starting burst, check if Queues got new data
                with self.lock:
                    if len(self.queue_emergency) > 0 or len(self.queue_normal) > 0 or \
                       len(self.req_emergency) > 0 or len(self.req_normal) > 0:
                        break # Break storage loop to handle new data
                
                # Perform Burst for this stored item
                self.send_pdu_burst(item['pdu'], is_new=False)