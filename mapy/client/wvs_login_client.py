from typing import Type

from .client_base import ClientBase

PendingLogin = Type["PendingLogin"]


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
        self.avatars = []

    async def login(self, username, password):
        resp, account = await (
            self.data.account(username=username, password=password).login()
        )

        if not resp:
            self.account = account
            self.logged_in = True
            return 0

        return resp

    async def load_avatars(self, world_id=None):
        if not self.account:
            self.avatars = []
            return

        self.avatars = await (
            self.data.account(id=self.account.id).get_entries(world_id=world_id)
        )

    @property
    def account_id(self):
        return getattr(self.account, "id", -1)
