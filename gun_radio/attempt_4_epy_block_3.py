import pmt
import time
from gnuradio import gr

class stop_and_wait_tx(gr.basic_block):
    def __init__(self, timeout=0.5):
        gr.basic_block.__init__(self,
            name="Stop-and-Wait TX",
            in_sig=[],
            out_sig=[]
        )
        # Message ports
        self.message_port_register_in(pmt.intern("in"))    # Data to send
        self.message_port_register_in(pmt.intern("ack"))   # ACK/NACK input
        self.message_port_register_out(pmt.intern("out"))  # Transmit PDU

        self.set_msg_handler(pmt.intern("in"), self.handle_new_packet)
        self.set_msg_handler(pmt.intern("ack"), self.handle_ack)

        self.last_packet = None
        self.waiting_ack = False
        self.timeout = timeout
        self.last_send_time = 0

    def handle_new_packet(self, msg):
        if not self.waiting_ack:
            self.last_packet = msg
            self.send_packet(msg)

    def handle_ack(self, msg):
        # Check if msg is ACK or NACK
        meta = pmt.car(msg)
        if pmt.dict_has_key(meta, pmt.intern("ack")):
            seq = pmt.to_long(pmt.dict_ref(meta, pmt.intern("ack"), pmt.PMT_NIL))
            print("ACK received for seq:", seq)
            self.waiting_ack = False
        elif pmt.dict_has_key(meta, pmt.intern("nack")):
            seq = pmt.to_long(pmt.dict_ref(meta, pmt.intern("nack"), pmt.PMT_NIL))
            print("NACK received for seq:", seq)
            # Retransmit immediately
            self.send_packet(self.last_packet)

    def send_packet(self, msg):
        self.message_port_pub(pmt.intern("out"), msg)
        self.waiting_ack = True
        self.last_send_time = time.time()

    def work(self, input_items, output_items):
        # Check timeout
        if self.waiting_ack and time.time() - self.last_send_time > self.timeout:
            print("Timeout! Retransmitting...")
            self.send_packet(self.last_packet)
        return 0
