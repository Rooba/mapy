from .character_stat import CharacterStat
from .avatar_look import AvatarLook

class CharacterEntry:
    def __init__(self, stats):
        self.stats = CharacterStat(**stats)
        
        gender = stats.get('gender')
        skin = stats.get('skin')
        face = stats.get('face')
        hair = stats.get('hair')
        
        self.look = AvatarLook(gender=gender, skin=skin,
                    face=face, hair=hair, weapon_sticker_id=0)

    @staticmethod
    def from_data(stats, equipped):
        entry = CharacterEntry(stats)
        entry.look.copy(equipped)
        return entry