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
            in_sig=None,   # message input
            out_sig=None   # message output
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
        # Convert incoming message to string
        if pmt.is_symbol(msg_pmt):
            msg_str = pmt.symbol_to_string(msg_pmt)
        elif pmt.is_u8vector(msg_pmt):
            msg_str = bytes(pmt.u8vector_elements(msg_pmt))
        else:
            # Convert any other type to string
            msg_str = str(msg_pmt)

        # Convert string to byte array
        byte_array = bytearray(msg_str, 'utf-8')

        # Convert to PMT u8vector
        msg_out = pmt.init_u8vector(len(byte_array), byte_array)

        # Wrap in PDU (meta, data)
        pdu = pmt.cons(pmt.make_dict(), msg_out)

        # Send message out
        self.message_port_pub(pmt.intern('out'), pdu)
