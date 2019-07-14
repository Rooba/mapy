from .client_base import ClientBase
from .entities import CharacterEntry

class WvsLoginClient(ClientBase):
    """LoginClient

    Parameters
    ----------

    parent: :class:`ServerBase`
        Parent server client is connecting to
    socket: :class:`Socket`
        Socket holding client - server connection
    name: str
        Name identifying type of client
    """

    def __init__(self, parent, socket):
        super().__init__(parent, socket)

        self.account = None
        self.server_id = None
        self.channel_id = None
        self.logged_in = False
        self.avatars = []

    async def login(self, username, password):
        ret = await self._parent.login(self, username, password)

        if not ret:
            self.logged_in = True

        return ret
    
    async def load_avatars(self):
        characters = await self._parent.data.get_characters(self.account.id)
        self.avatars += characters

    @property
    def account_id(self):
        return self.account.id if getattr(self.account, 'id') else -1
