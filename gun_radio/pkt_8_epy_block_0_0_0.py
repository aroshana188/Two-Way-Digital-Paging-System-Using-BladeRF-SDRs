import pmt
from gnuradio import gr

class TaggedStreamToFile(gr.basic_block):
    """
    Writes incoming PDUs (Tagged Stream converted to PDU) into a file,
    including metadata. Appends all incoming PDUs sequentially.
    """

    def __init__(self, filename="C:/Users/arosh/OneDrive/Desktop/output.txt"):
        gr.basic_block.__init__(
            self,
            name="TaggedStreamToFile",
            in_sig=[],
            out_sig=[]
        )
        self.filename = filename

        # Register message input port
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)

    def handle_msg(self, msg):
        # msg is a PDU = (metadata dict, data vector)
        meta = pmt.car(msg)        # metadata dictionary
        data = pmt.cdr(msg)        # u8vector payload

        # Convert data to Python bytes
        data_bytes = bytes(pmt.u8vector_elements(data))

        # Convert metadata to string
        try:
            meta_str = pmt.write_string(meta)
        except:
            meta_str = str(meta)

        # Append to file
        with open(self.filename, "ab") as f:
            f.write(b"==== NEW PACKET ====\n")
            f.write(f"Metadata: {meta_str}\n".encode())
            f.write(b"Payload: " + data_bytes + b"\n\n")
