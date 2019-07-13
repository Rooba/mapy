from .client_base import ClientBase


class WvsCenterClient(ClientBase):
    """CenterClient

    Parameters
    ----------

    parent: `ServerBase`
        Parent server client is connecting to
    socket: `socket`
        Socket holding client - server connection
    name: str
        Name identifying type of client
    """

    def __init__(self, parent, socket, port=None):
        super().__init__(parent, socket)

        self._world = None
        self._id = None
        self._population = 0
        self._type = None

    @property
    def population(self):
        return self._population

    @population.setter
    def population(self, value):
        self._population = value

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, value):
        self._world = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value
