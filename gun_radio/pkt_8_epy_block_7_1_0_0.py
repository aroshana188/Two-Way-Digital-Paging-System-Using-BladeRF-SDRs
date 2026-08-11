"""
Embedded Python Block: Address & Type Filter (Receiver Gatekeeper)
Function:
1. Filters packets based on Destination IP.
2. Sorts Traffic:
   - Type 'M' (Message) -> pdu_out (To Depacketizer/Display)
   - Type 'A' (ACK)     -> ack_out (To PDU Storage to clear buffer)
"""
import numpy as np
from gnuradio import gr
import pmt
import socket

class addr_type_filter(gr.basic_block):
    def __init__(self, my_ip="192.168.1.20"):
        """
        my_ip: The IP address of THIS receiver. 
               Packets not destined for this IP will be dropped.
        """
        gr.basic_block.__init__(self,
            name="Address & Type Filter",
            in_sig=None,
            out_sig=None)

        self.my_ip_str = my_ip
        
        # Convert IP string to 4-byte list for comparison
        try:
            self.my_ip_bytes = list(socket.inet_aton(self.my_ip_str))
        except OSError:
            print(f"[Filter] Error: Invalid IP {my_ip}")
            self.my_ip_bytes = [0, 0, 0, 0]

        # Register Ports
        self.message_port_register_in(pmt.intern("pdu_in"))
        
        # Output 1: Valid Messages (Goes to Depacketizer)
        self.message_port_register_out(pmt.intern("pdu_out"))
        
        # Output 2: Valid ACKs (Goes back to Transmitter's PDU Storage)
        self.message_port_register_out(pmt.intern("ack_out"))
        
        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            payload = pmt.cdr(msg)
            data_bytes = list(pmt.u8vector_elements(payload))
            
            # --- 1. Safety Check (Min Header Size) ---
            # Header is 12 bytes. If less, it's garbage.
            if len(data_bytes) < 12:
                return

            # --- 2. Check Destination Address (Bytes 0-3) ---
            dest_received = data_bytes[0:4]
            
            if dest_received != self.my_ip_bytes:
                # Packet is not for me -> Drop it
                return

            # --- 3. Extract Type Info ---
            # Header: [Dst(4) | Src(4) | Type(1) | MsgID(1) | Seq(1) | Prio(1)]
            # Indices: 0-3      4-7      8         9         10      11
            
            pkt_type = data_bytes[8]
            msg_id   = data_bytes[9]
            seq_or_rn = data_bytes[10] # SeqNum for Msg, RN for ACK

            # --- 4. Logic Branch ---
            
            # === CASE: MESSAGE ('M') ===
            if pkt_type == ord('M'):
                # User Requirement: Send the WHOLE PDU to pdu_out
                self.message_port_pub(pmt.intern("pdu_out"), msg)

            # === CASE: ACKNOWLEDGMENT ('A') ===
            elif pkt_type == ord('A'):
                # User Requirement: Send MsgID and RN to ack_out
                # The PDU Storage block expects a PDU payload of [MsgID, RN]
                
                ack_payload = [msg_id, seq_or_rn]
                
                # Create PDU
                out_pmt = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(2, ack_payload))
                self.message_port_pub(pmt.intern("ack_out"), out_pmt)
                
                # print(f"[Filter] Received ACK for Msg {msg_id}, RN {seq_or_rn}")

        except Exception as e:
            print(f"[Filter] Error: {e}")