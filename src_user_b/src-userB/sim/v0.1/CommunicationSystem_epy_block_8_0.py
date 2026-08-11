from gnuradio import gr
import pmt
from collections import deque
import threading
import time
import zlib

class crc_block(gr.basic_block):
    """
    CRC Block (PDU-based)
    ---------------------
    TX: Prepend CRC32 to data payload and forward PDU.
    RX: Verify CRC32 at start of data; strip CRC and forward if valid.
    """

    def __init__(self):
        gr.basic_block.__init__(self, name="CRC_PDU", in_sig=[], out_sig=[])

        # Ports
        self.message_port_register_in(pmt.intern("in_tx"))
        self.set_msg_handler(pmt.intern("in_tx"), self.handle_in_tx)
        self.message_port_register_in(pmt.intern("in_rx"))
        self.set_msg_handler(pmt.intern("in_rx"), self.handle_in_rx)

        self.message_port_register_out(pmt.intern("out_tx"))
        self.message_port_register_out(pmt.intern("out_rx"))

        # Queues
        self.tx_queue = deque()
        self.rx_queue = deque()

        # Threads
        self.running = True
        self.tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self.rx_loop, daemon=True)
        self.tx_thread.start()
        self.rx_thread.start()

    # ---------------- Handlers ----------------
    def handle_in_tx(self, pdu):
        if pmt.is_pair(pdu):
            self.tx_queue.append(pdu)

    def handle_in_rx(self, pdu):
        if pmt.is_pair(pdu):
            self.rx_queue.append(pdu)

    # ---------------- TX loop ----------------
    def tx_loop(self):
        while self.running:
            if self.tx_queue:
                pdu = self.tx_queue.popleft()
                meta = pmt.car(pdu)  # empty
                data = list(pmt.u8vector_elements(pmt.cdr(pdu)))

                # Compute CRC32 over the entire payload
                crc_value = zlib.crc32(bytes(data)) & 0xFFFFFFFF
                crc_bytes = [(crc_value >> 24) & 0xFF,
                             (crc_value >> 16) & 0xFF,
                             (crc_value >> 8) & 0xFF,
                             crc_value & 0xFF]

                # Prepend CRC to data
                data_with_crc = crc_bytes + data
                data_pmt = pmt.init_u8vector(len(data_with_crc), data_with_crc)

                # Forward PDU (meta empty, data with CRC)
                self.message_port_pub(pmt.intern("out_tx"), pmt.cons(pmt.make_dict(), data_pmt))
            else:
                time.sleep(0.01)

    # ---------------- RX loop ----------------
    def rx_loop(self):
        while self.running:
            if self.rx_queue:
                pdu = self.rx_queue.popleft()
                meta = pmt.car(pdu)  # empty
                data = list(pmt.u8vector_elements(pmt.cdr(pdu)))
                if len(data) < 4:
                    continue  # invalid frame

                # Extract CRC and payload
                recv_crc_bytes = data[:4]
                payload = data[4:]
                recv_crc = (recv_crc_bytes[0] << 24) | (recv_crc_bytes[1] << 16) | \
                           (recv_crc_bytes[2] << 8) | recv_crc_bytes[3]

                # Verify CRC
                computed_crc = zlib.crc32(bytes(payload)) & 0xFFFFFFFF
                if recv_crc == computed_crc:
                    # CRC OK: forward PDU without CRC
                    payload_pmt = pmt.init_u8vector(len(payload), payload)
                    self.message_port_pub(pmt.intern("out_rx"), pmt.cons(pmt.make_dict(), payload_pmt))
                # else: silently drop
            else:
                time.sleep(0.01)

    # ---------------- Stop ----------------
    def stop(self):
        self.running = False
        self.tx_thread.join()
        self.rx_thread.join()
        return True