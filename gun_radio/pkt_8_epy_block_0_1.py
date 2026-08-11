"""
Embedded Python Block: ACK Repeater (Aggressive Flush)
Function: 
1. Repeats ACKs 'N' times (Burst).
2. AGGRESSIVE FLUSH: If a new MsgID or newer RN comes, 
   it DELETES the entire old queue immediately to prioritize the latest status.
"""
import numpy as np
from gnuradio import gr
import pmt
import threading
import time

class ack_repeater(gr.basic_block):
    def __init__(self, num_repeats=5, delay=0.05):
        """
        num_repeats: How many times to burst the ACK.
        delay: Time between burst packets.
        """
        gr.basic_block.__init__(self,
            name="ACK Repeater",
            in_sig=None,
            out_sig=None)

        self.num_repeats = num_repeats
        self.delay = delay
        
        self.message_port_register_in(pmt.intern("in"))
        self.message_port_register_out(pmt.intern("out"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)
        
        # State
        self.queue = []
        self.current_task = None
        self.preempt_flag = False 
        
        self.lock = threading.Lock()
        self.running = True
        self.worker = threading.Thread(target=self.process_loop, daemon=True)
        self.worker.start()

    def get_header_info(self, u8_list):
        try:
            # Header: [Dst(4)|Src(4)|Type(1)|MsgID(1)|RN(1)|Prio(1)]
            # MsgID is at index 9, RN at index 10
            msg_id = u8_list[9]
            rn_num = u8_list[10]
            return msg_id, rn_num
        except:
            return 0, 0

    def handle_msg(self, msg):
        """
        Receives new ACK. 
        If it's newer than what we are sending, FLUSH everything and start this one.
        """
        with self.lock:
            payload = pmt.cdr(msg)
            if not pmt.is_u8vector(payload): return
            u8_list = list(pmt.u8vector_elements(payload))
            if len(u8_list) < 12: return

            new_msg_id, new_rn = self.get_header_info(u8_list)
            
            new_task = {
                'pdu': msg,
                'msg_id': new_msg_id,
                'rn': new_rn
            }

            # --- AGGRESSIVE LOGIC ---
            # Do we have a current task?
            if self.current_task:
                curr_id = self.current_task['msg_id']
                curr_rn = self.current_task['rn']
                
                # Condition 1: Is this a completely NEW Message ID?
                is_new_msg = (new_msg_id != curr_id)
                
                # Condition 2: Is this the SAME Message but a NEWER Request Number?
                is_newer_rn = (new_msg_id == curr_id and new_rn > curr_rn)
                
                if is_new_msg or is_newer_rn:
                    # 1. Clear the waiting queue completely (Delete old ACKs)
                    self.queue.clear()
                    
                    # 2. Trigger interrupt for the worker thread
                    self.preempt_flag = True
                    
                    # 3. Queue this new task as the priority
                    self.queue.append(new_task)
                    # Optional Debug:
                    # print(f"[ACK Rpt] FLUSHING! Stopped {curr_id}:{curr_rn} -> Starting {new_msg_id}:{new_rn}")
                else:
                    # It's an old or duplicate ACK. Ignore it to save bandwidth.
                    pass
            else:
                # We are idle. Just add it to the queue.
                # If queue has items, check if this one is newer than the last one in queue
                if len(self.queue) > 0:
                    last_task = self.queue[-1]
                    last_id = last_task['msg_id']
                    last_rn = last_task['rn']
                    
                    if (new_msg_id != last_id) or (new_msg_id == last_id and new_rn > last_rn):
                        self.queue.clear()
                        self.queue.append(new_task)
                else:
                    self.queue.append(new_task)

    def process_loop(self):
        while self.running:
            task = None
            
            # Get next task
            with self.lock:
                if len(self.queue) > 0:
                    task = self.queue.pop(0)
                    self.current_task = task
                    self.preempt_flag = False # Reset flag for new task
                else:
                    self.current_task = None

            # If nothing to do, sleep
            if task is None:
                time.sleep(0.01)
                continue

            # --- BURST LOOP ---
            for i in range(self.num_repeats):
                # Check for interrupt signal from handle_msg
                if self.preempt_flag:
                    break 
                
                # Send
                self.message_port_pub(pmt.intern("out"), task['pdu'])
                time.sleep(self.delay)