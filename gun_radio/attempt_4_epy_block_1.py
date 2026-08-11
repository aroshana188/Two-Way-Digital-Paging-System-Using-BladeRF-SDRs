# StopAndWaitReceiver.py
# PDU Python Block for GNU Radio
# Inputs: Received packets (PDUs)
# Outputs: ACKs (PDUs), Forwarded packets to file / next block

import pmt
from gnuradio import gr

class blk(gr.basic_block):
    """Stop-and-Wait ARQ Receiver"""
    
    def __init__(self):
        gr.basic_block.__init__(
            self,
            name="StopAndWaitReceiver",
            in_sig=[],
            out_sig=[]
        )

        # Message ports
        self.message_port_register_in(pmt.intern("pkt_in"))
        self.set_msg_handler(pmt.intern("pkt_in"), self.packet_handler)
        self.message_port_register_out(pmt.intern("ack_out"))
        self.message_port_register_out(pmt.intern("payload_out"))

        self.expected_seq = 0

    # Handle incoming packet
    def packet_handler(self, pdu):
        pkt_vec = pmt.u8vector_elements(pmt.cdr(pdu))
        if len(pkt_vec) < 1:
            return
        seq = pkt_vec[0]
        payload = pkt_vec[1:]

        # Simple CRC check placeholder (you can implement real CRC here)
        crc_ok = True  # Replace with actual CRC check

        if crc_ok and seq == self.expected_seq % 256:
            print(f"Received correct packet seq={seq}")
            # Forward payload to next block
            self.message_port_pub(pmt.intern("payload_out"), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(payload), payload)))
            # Send ACK
            ack_vec = [seq]
            self.message_port_pub(pmt.intern("ack_out"), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(ack_vec), ack_vec)))
            self.expected_seq += 1
        else:
            print(f"Packet seq={seq} incorrect or duplicate. Ignoring.")
            # Optionally, you could resend last ACK
