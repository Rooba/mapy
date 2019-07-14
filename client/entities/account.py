from dataclasses import dataclass

@dataclass
class Account:
    id: int
    username: str
    password: str
    gender: int = 0
    ban: int = 0
    admin: int = 0
    creation: str = "typing.Any"
    last_login: str = "typing.Any"