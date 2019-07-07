from .client_base import ClientBase

class WvsLoginClient(ClientBase):
    """LoginClient

    Parameters
    ----------

    parent: `ServerBase`
        Parent server client is connecting to
    socket: `socket`
        Socket holding client - server connection
    name: str
        Name identifying type of client
    """

    def __init__(self, parent, socket):
        super().__init__(parent, socket, "Login Client")
        