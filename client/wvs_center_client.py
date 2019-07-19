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

        self.world = None
        self.id = None
        self.population = 0
        self.type = None