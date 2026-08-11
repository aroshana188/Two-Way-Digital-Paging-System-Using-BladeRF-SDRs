import pmt
from gnuradio import gr

class MessageToByteArray(gr.basic_block):
    """
    Converts incoming messages to byte array PDUs.
    Compatible with Message Strobe and Message Debug.
    """
    def __init__(self):
        gr.basic_block.__init__(
            self,
            name="MessageToByteArray",
            in_sig=None,
            out_sig=None
        )

        # Register message ports
        self.message_port_register_in(pmt.intern('in'))
        self.message_port_register_out(pmt.intern('out'))

        # Set handler for incoming messages
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg_pmt):
        """
        Handle incoming PMT messages and convert them to byte array PDUs.
        """
        # Case 1: PMT symbol (string-like)
        if pmt.is_symbol(msg_pmt):
            data_bytes = bytearray(pmt.symbol_to_string(msg_pmt), 'utf-8')

        # Case 2: Already a u8vector (raw bytes)
        elif pmt.is_u8vector(msg_pmt):
            data_bytes = bytearray(pmt.u8vector_elements(msg_pmt))

        # Fallback: convert anything else to string then encode
        else:
            data_bytes = bytearray(str(msg_pmt), 'utf-8')

        # Convert to PMT u8vector
        msg_out = pmt.init_u8vector(len(data_bytes), data_bytes)

        # Wrap as PDU (meta dict, data vector)
        pdu = pmt.cons(pmt.make_dict(), msg_out)

        # Publish PDU
        self.message_port_pub(pmt.intern('out'), pdu)
