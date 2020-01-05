from .client_base import ClientBase


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
        response, account = await self.data.\
            account(username=username, password=password).login()

        if not response:
            self.account = account
            self.logged_in = True
            return 0

        return response

    async def load_avatars(self, world_id=None):
        self.avatars = await self.data\
            .account(id=self.account.id)\
                .get_characters(world_id=world_id)

    @property
    def account_id(self):
        return self.account.id if getattr(self.account, 'id') else - 1
