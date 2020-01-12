class PendingLogin:
    def __init__(self, character, account, requested):
        self.character = character
        self.char_id = character.id
        self.account = account
        self.requested = requested
        self.migrated = False