"""
Embedded Python Block: ACK Repeater (Burst Feedback)
Function: 
1. Repeats ACKs 'N' times to ensure the Sender hears them.
2. Smart Preemption: If a newer Request Number (RN) arrives for the SAME message, 
   it stops sending the old RN immediately and starts the new one.
"""
import numpy as np
from gnuradio import gr
import pmt
import threading
import time

class ack_repeater(gr.basic_block):
    def __init__(self, num_repeats=5, delay=0.05):
        """
        num_repeats: How many times to send each ACK.
        delay: Time (seconds) between repeats.
        """
        gr.basic_block.__init__(self,
            name="ACK Repeater",
            in_sig=None,
            out_sig=None)

        self.num_repeats = num_repeats
        self.delay = delay
        
        # --- PORTS ---
        self.message_port_register_in(pmt.intern("in"))   # From ACK Generator
        self.message_port_register_out(pmt.intern("out")) # To CRC Append / Mux
        
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)
        
        # --- STATE MANAGEMENT ---
        self.queue = []           # Queue for ACKs waiting to be sent
        self.current_task = None  # Info about what is currently bursting
        self.preempt_flag = False # Flag to interrupt the current burst
        
        self.lock = threading.Lock()
        self.running = True
        
        # Start Worker
        self.worker = threading.Thread(target=self.process_loop, daemon=True)
        self.worker.start()

    def get_header_info(self, u8_list):
        # Header: [Dst(4)|Src(4)|Type(1)|MsgID(1)|RN(1)|Prio(1)]
        try:
            msg_id = u8_list[9]
            rn_num = u8_list[10]
            return msg_id, rn_num
        except:
            return 0, 0

    def handle_msg(self, msg):
        """
        Receives new ACK from Generator.
        Decides whether to Queue it or Preempt the current burst.
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
                'rn': new_rn,
                'raw_bytes': u8_list
            }

            # --- DECISION LOGIC ---
            if self.current_task is not None:
                curr_msg_id = self.current_task['msg_id']
                curr_rn     = self.current_task['rn']
                
                # Check Preemption Condition:
                # Same Message ID AND Higher Request Number
                if (new_msg_id == curr_msg_id) and (new_rn > curr_rn):
                    # PREEMPT! Stop current loop.
                    self.preempt_flag = True
                    # Insert this new important task at the FRONT of the queue
                    self.queue.insert(0, new_task)
                    # print(f"[ACK Rpt] Preempting RN {curr_rn} for RN {new_rn}")
                else:
                    # Different Msg OR Older RN -> Wait your turn
                    self.queue.append(new_task)
            else:
                # Nothing happening currently, just queue it
                self.queue.append(new_task)

    def process_loop(self):
        while self.running:
            # 1. Get Next Task
            task = None
            with self.lock:
                if len(self.queue) > 0:
                    task = self.queue.pop(0)
                    self.current_task = task
                    self.preempt_flag = False # Reset flag for new task
                else:
                    self.current_task = None

            # 2. If no task, sleep and retry
            if task is None:
                time.sleep(0.01)
                continue

            # 3. Burst Loop
            # Send 'num_repeats' times, but check for preemption every time
            for i in range(self.num_repeats):
                # Check Interrupt
                if self.preempt_flag:
                    break # Stop sending this old ACK immediately
                
                # Send
                self.message_port_pub(pmt.intern("out"), task['pdu'])
                
                # Wait
                time.sleep(self.delay)
            
            # Burst finished (or preempted). Loop back to check queue.