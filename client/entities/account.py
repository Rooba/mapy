class Account:
    def __init__(self, **data):
        self.id = data.get('id')
        self.username = data.get('username')
        self.password = data.get('password')
        self.gender = data.get('gender', 0)
        self.ban = data.get('ban', 0)
        self.admin = data.get('admin', 0)
        self.creation = data.get('creation', None)
        self.last_login = data.get('last_login', None)
        self.last_ip = data.get('last_ip', None)