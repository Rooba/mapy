class Channel:
    def __init__(self, packet):
        self._id = packet.decode_byte()
        self._port = packet.decode_short()
        self._population = packet.decode_int()