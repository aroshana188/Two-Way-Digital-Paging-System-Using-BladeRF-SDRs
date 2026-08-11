"""
Embedded Python Block: PDU Queue & Storage (Strict Emergency Priority)
Logic: 
1. Priority Queues (Emergency > Requests > Normal)
2. Preemption: If sending 'Normal' and 'Emergency' appears (New or Request), STOP immediately.
3. Burst Send: Transmit Packet N times, checking for interrupts every time.
"""
import numpy as np
from gnuradio import gr
import pmt
import time
import threading

class PDUQueueStorage(gr.basic_block):
    def __init__(self, timeout=1.0, max_retries=50):
        """
        timeout: Delay between retransmissions in a burst.
        max_retries: Number of times to send in one burst.
        """
        gr.basic_block.__init__(self,
            name="PDU Queue & Storage",
            in_sig=None,
            out_sig=None)

        self.timeout = timeout
        self.max_retries = max_retries
        self.running = True

        # --- QUEUES (Strict Priority Order) ---
        self.queue_emergency = []  # 1. New Emergency Packets
        self.req_emergency = []    # 2. Emergency Retransmissions (triggered by ACKs)
        self.req_normal = []       # 3. Normal Retransmissions
        self.queue_normal = []     # 4. New Normal Packets
        self.storage = []          # 5. Persistent Storage (All un-ACKed packets)
        
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
        """Handle Incoming New Packet from User"""
        with self.lock:
            payload = pmt.cdr(msg)
            u8_list = list(pmt.u8vector_elements(payload))
            _, _, prio_byte = self.get_header_info(u8_list)
            
            # STRICT SORTING
            if prio_byte == ord('E'):
                self.queue_emergency.append(u8_list)
                # print("[Queue] New EMERGENCY Packet Received!")
            else:
                self.queue_normal.append(u8_list)

    def handle_rn(self, msg):
        """Handle Feedback (ACK/Request) from Receiver"""
        with self.lock:
            try:
                payload = pmt.cdr(msg)
                rn_data = list(pmt.u8vector_elements(payload))
                
                if len(rn_data) < 2: return
                
                req_msg_id = rn_data[0]
                req_seq_num = rn_data[1]
                
                # 1. CLEANUP (Cumulative ACK): Remove successfully received packets
                # (Same MsgID but LOWER SeqNum means receiver has them)
                self.storage = [p for p in self.storage if not (p['msg_id'] == req_msg_id and p['seq'] < req_seq_num)]
                
                # 2. RETRANSMISSION REQUEST (NACK):
                # Receiver is asking for 'req_seq_num'. Find it and queue it ASAP.
                for item in self.storage:
                    if item['msg_id'] == req_msg_id and item['seq'] == req_seq_num:
                        pdu_copy = list(item['pdu'])
                        
                        # PRIORITY CHECK: Is the missing packet Emergency?
                        if item['prio'] == ord('E'):
                            # HIGH PRIORITY REQUEST
                            self.req_emergency.append(pdu_copy)
                            # print(f"[Queue] Emergency Retransmission Requested! (Seq {req_seq_num})")
                        else:
                            self.req_normal.append(pdu_copy)
                        break 
            except Exception as e:
                print(f"[Queue] RN Error: {e}")

    def send_pdu_burst(self, pdu_list, is_new=False):
        """
        Sends packet multiple times.
        CRITICAL: Checks for Emergency Interrupts before every single send.
        """
        
        # 1. ADD TO STORAGE (If New)
        if is_new:
            with self.lock:
                msg_id, seq_num, prio = self.get_header_info(pdu_list)
                exists = any(p['msg_id'] == msg_id and p['seq'] == seq_num for p in self.storage)
                if not exists:
                    self.storage.append({
                        'pdu': pdu_list,
                        'msg_id': msg_id,
                        'seq': seq_num,
                        'prio': prio
                    })

        # 2. BURST LOOP
        for i in range(self.max_retries):
            
            # --- CHECK A: HAS IT BEEN ACKED? ---
            # If receiver got it, stop wasting time.
            with self.lock:
                msg_id, seq_num, _ = self.get_header_info(pdu_list)
                still_exists = any(p['msg_id'] == msg_id and p['seq'] == seq_num for p in self.storage)
                if not still_exists:
                    return # Packet cleared, stop burst.

            # --- CHECK B: EMERGENCY INTERRUPT ---
            # If we are sending Normal, but Emergency work appeared -> ABORT.
            if self.check_priority_interrupt(current_pdu=pdu_list):
                return # Stop this burst immediately to handle Emergency.

            # --- SEND ---
            out_pmt = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(pdu_list), pdu_list))
            self.message_port_pub(pmt.intern("pdu_out"), out_pmt)
            
            # --- WAIT ---
            time.sleep(self.timeout)

    def check_priority_interrupt(self, current_pdu):
        """Returns True if a higher priority task exists"""
        _, _, prio = self.get_header_info(current_pdu)
        
        # Only NORMAL packets can be interrupted
        if prio == ord('N'):
            with self.lock:
                # If ANY Emergency task (New or Request) is waiting...
                if len(self.queue_emergency) > 0 or len(self.req_emergency) > 0:
                    # print("[Queue] Normal Burst INTERRUPTED for Emergency!")
                    return True
        return False

    def process_loop(self):
        while self.running:
            target_pdu = None
            is_new = False
            
            # --- 1. CHECK QUEUES (Highest to Lowest) ---
            # Always check Emergency first.
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
            
            # If we found something in the high-priority queues, handle it
            if target_pdu:
                self.send_pdu_burst(target_pdu, is_new)
                continue # Restart loop to check for more Emergency items
            
            # --- 2. STORAGE LOOP (Round Robin / Idle) ---
            # If queues are empty, we cycle through storage (re-sending un-ACKed items)
            with self.lock:
                storage_snapshot = list(self.storage)
            
            if len(storage_snapshot) == 0:
                time.sleep(0.1) 
                continue

            for item in storage_snapshot:
                # Before starting a stored item burst, check queues again
                with self.lock:
                    if len(self.queue_emergency) > 0 or len(self.queue_normal) > 0 or \
                       len(self.req_emergency) > 0 or len(self.req_normal) > 0:
                        break # Break out of storage loop to handle new queue items
                
                # Perform Burst
                self.send_pdu_burst(item['pdu'], is_new=False)