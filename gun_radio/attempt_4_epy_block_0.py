# StopAndWaitSender.py
# PDU Python Block for GNU Radio
# Inputs: ACKs (PDUs)
# Outputs: Packets to transmit (PDUs)

import pmt
from gnuradio import gr
import time

class blk(gr.basic_block):
    """Stop-and-Wait ARQ Sender"""
    
    def __init__(self, timeout_ms=500):
        gr.basic_block.__init__(
            self,
            name="StopAndWaitSender",
            in_sig=[],
            out_sig=[]
        )

        # Message ports
        self.message_port_register_in(pmt.intern("ack_in"))
        self.set_msg_handler(pmt.intern("ack_in"), self.ack_handler)
        self.message_port_register_out(pmt.intern("pkt_out"))

        # Internal variables
        self.queue = []          # List of packets waiting to be sent
        self.current_pkt = None  # Packet currently in transmission
        self.seq_num = 0         # Sequence number
        self.timeout_ms = timeout_ms
        self.last_send_time = None

    # Receive new packet to send
    def recv_msg(self, pdu):
        meta = pmt.car(pdu)
        vec = pmt.cdr(pdu)
        self.queue.append(vec)
        # If nothing is being sent, send immediately
        if self.current_pkt is None:
            self.send_next_packet()

    # Send next packet from queue
    def send_next_packet(self):
        if len(self.queue) == 0:
            self.current_pkt = None
            return

        pkt = self.queue.pop(0)
        # Prepend sequence number (1 byte)
        pkt_with_seq = bytes([self.seq_num % 256]) + bytearray(pkt)
        self.current_pkt = pkt_with_seq
        self.last_send_time = time.time()
        # Send as PDU
        self.message_port_pub(pmt.intern("pkt_out"), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(pkt_with_seq), pkt_with_seq)))
        print(f"Sent packet seq={self.seq_num}")
        # Increment seq_num for next packet after ACK
        # Will increment after receiving ACK

    # ACK handler
    def ack_handler(self, ack_pdu):
        ack_vec = pmt.u8vector_elements(pmt.cdr(ack_pdu))
        if len(ack_vec) == 0:
            return
        ack_seq = ack_vec[0]
        if ack_seq == self.seq_num % 256:
            print(f"ACK received for seq={ack_seq}")
            self.seq_num += 1
            self.current_pkt = None
            self.send_next_packet()

    # Called periodically by GRC scheduler
    def general_work(self, input_items, output_items):
        # Check timeout
        if self.current_pkt is not None:
            elapsed_ms = (time.time() - self.last_send_time) * 1000
            if elapsed_ms > self.timeout_ms:
                print(f"Timeout, resending seq={self.seq_num}")
                self.last_send_time = time.time()
                self.message_port_pub(pmt.intern("pkt_out"), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(self.current_pkt), self.current_pkt)))
        return 0
