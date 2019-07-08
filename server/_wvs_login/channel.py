class Channel:
    def __init__(self, packet):
        self._id = packet.decode_byte()
        self._port = packet.decode_short()
        self._population = packet.decode_int()
    
    @property
    def population(self):
        return self._population

    @population.setter
    def population(self, value):
        self._population = value