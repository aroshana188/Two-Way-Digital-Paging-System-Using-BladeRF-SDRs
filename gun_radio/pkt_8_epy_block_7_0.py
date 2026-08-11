"""
Embedded Python Block: Sequence & Msg Decoder (Fixed Void Msgs)
Function:
1. Reassembles messages from packets.
2. Tracks Sequence Numbers (RN).
3. Sends 'Draft ACKs' to the ACK Generator.
4. Outputs Reassembled Text to GUI.
"""
import numpy as np
from gnuradio import gr
import pmt
import struct

class sequence_decoder(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Sequence & Msg Decoder",
            in_sig=None,
            out_sig=None)

        # Inputs/Outputs
        self.message_port_register_in(pmt.intern("pdu_in")) 
        self.message_port_register_out(pmt.intern("to_ack")) # To ACK Generator
        self.message_port_register_out(pmt.intern("to_app")) # To GUI

        self.set_msg_handler(pmt.intern("pdu_in"), self.handle_msg)
        self.sessions = {}

    def parse_header(self, u8_list):
        dst_ip = tuple(u8_list[0:4])
        src_ip = tuple(u8_list[4:8])
        pkt_type = u8_list[8]
        msg_id   = u8_list[9]
        seq_num  = u8_list[10]
        prio     = u8_list[11]
        payload  = u8_list[12:]
        return dst_ip, src_ip, pkt_type, msg_id, seq_num, prio, payload

    def send_ack(self, dst_ip_me, src_ip_sender, msg_id, rn_request, prio):
        """
        Prepares 'Draft' ACK.
        Format: [Dst=Me | Src=Sender | Type=M | MsgID | RN | Prio]
        NOTE: addresses are NOT swapped here. ACK Generator will do it.
        """
        ack_header = []
        ack_header.extend(list(dst_ip_me))      # Keep Dst = Me
        ack_header.extend(list(src_ip_sender))  # Keep Src = Sender
        ack_header.append(ord('M'))             # Type placeholder (Generator sets 'A')
        ack_header.append(msg_id)
        ack_header.append(rn_request)           # The requested SN (RN)
        ack_header.append(prio)
        
        padding = [0] * 16 
        ack_packet = ack_header + padding
        
        out_pmt = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(ack_packet), ack_packet))
        self.message_port_pub(pmt.intern("to_ack"), out_pmt)

    def handle_msg(self, msg):
        try:
            pdu_content = pmt.cdr(msg)
            u8_list = list(pmt.u8vector_elements(pdu_content))
            if len(u8_list) < 12: return

            dst_ip, src_ip, pkt_type, msg_id, seq_num, prio, payload = self.parse_header(u8_list)
            session_key = (src_ip, msg_id)

            if session_key not in self.sessions:
                self.sessions[session_key] = {'rn': 0, 'buffer': {}, 'eom_received': False}
            state = self.sessions[session_key]

            if seq_num == 99:
                state['eom_received'] = True

            # Case 1: Old Packet (Already have it) -> Ack current RN
            if seq_num < state['rn'] and seq_num != 99:
                self.send_ack(dst_ip, src_ip, msg_id, state['rn'], prio)
                return

            # Case 2: New Packet -> Store it
            if seq_num != 99:
                state['buffer'][seq_num] = payload

            # Advance RN (Cumulative)
            while state['rn'] in state['buffer']:
                state['rn'] += 1

            # --- COMPLETION CHECK (UPDATED) ---
            is_complete = False
            if state['eom_received']:
                # FIX: Ensure we actually have data (rn > 0) to avoid void messages
                if len(state['buffer']) == state['rn'] and state['rn'] > 0:
                    is_complete = True

            if is_complete:
                # Send Success (RN=100)
                self.send_ack(dst_ip, src_ip, msg_id, 100, prio)
                self.reassemble_and_send(state['buffer'], src_ip, dst_ip, prio)
                del self.sessions[session_key]
            else:
                # Request Next Needed Packet (RN)
                self.send_ack(dst_ip, src_ip, msg_id, state['rn'], prio)

        except Exception as e:
            print(f"[Decoder] Error: {e}")

    def reassemble_and_send(self, buffer, src_ip, dst_ip, prio):
        try:
            sorted_seqs = sorted(buffer.keys())
            full_msg_bytes = []
            for s in sorted_seqs:
                full_msg_bytes.extend(buffer[s])

            clean_bytes = [b for b in full_msg_bytes if b != 0]
            msg_text = "".join([chr(b) for b in clean_bytes])

            src_str = ".".join(map(str, src_ip))
            dst_str = ".".join(map(str, dst_ip))
            prio_char = chr(prio) 
            
            # Format: [INFO] SRC:x.x.x.x IP:x.x.x.x MSG:[E] >> Hello
            final_string = f"[INFO] SRC:{src_str} IP:{dst_str} MSG:[{prio_char}] >> {msg_text}"
            
            out_pmt = pmt.cons(pmt.PMT_NIL, pmt.string_to_symbol(final_string))
            self.message_port_pub(pmt.intern("to_app"), out_pmt)
            print(f"[Decoder] Reassembled: {final_string}")

        except Exception as e:
            print(f"[Decoder] Reassembly Error: {e}")