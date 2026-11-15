"""Byte-preserving output for legacy PS/PDF generators."""
import io
import os


class ByteBuffer(io.BytesIO):
    """Accept old single-byte strings while counting actual PDF byte offsets."""
    def __init__(self,offset=0):
        super().__init__();self.offset=offset

    def write(self,data):
        return super().write(data.encode('latin-1') if isinstance(data,str) else data)

    def tell(self):return self.offset+super().tell()


def stream_offset(destination):
    if isinstance(destination,(str,os.PathLike)):return 0
    if isinstance(destination,io.TextIOBase) and not isinstance(destination,io.StringIO):
        raise TypeError('Use a binary output file; text encoding/newline conversion invalidates vector output.')
    try:return destination.tell()
    except (AttributeError,OSError):return 0


def write_bytes(destination,data):
    """Own/close paths only. StringIO is a legacy Latin-1 in-memory view."""
    if isinstance(destination,(str,os.PathLike)):
        with open(destination,'wb') as output:output.write(data)
    elif isinstance(destination,io.StringIO):destination.write(data.decode('latin-1'))
    elif isinstance(destination,io.TextIOBase):
        raise TypeError('Use a binary output file; text encoding/newline conversion invalidates vector output.')
    else:destination.write(data)
