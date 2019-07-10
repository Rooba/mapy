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
        super().__init__(parent, socket)

        self._account = None

    async def login(self, username, password):
        ret = await self._parent.login(self, username, password)

        if ret == 0:
            self.logged_in = True
        
        return ret

    @property
    def account(self):
        return self._account
    
    @account.setter
    def account(self, value):
        self._account = value

    @property
    def account_id(self):
        return self._account.id if getattr(self._account, 'id') else -1
    
