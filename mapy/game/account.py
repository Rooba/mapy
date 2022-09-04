class Account:

    def __init__(
        self,
        id=0,
        username="",
        password="",
        gender=0,
        creation="",
        last_login="",
        last_ip="",
        ban=0,
        admin=0,
        last_connected_world=0,
    ):
        self.id: int = id
        self.username: str = username
        self.password: str = password
        self.gender: int = gender
        self.creation: str = creation
        self.last_login: str = last_login
        self.last_ip: str = last_ip
        self.ban: int = ban
        self.admin: int = admin
        self.last_connected_world: int = last_connected_world
