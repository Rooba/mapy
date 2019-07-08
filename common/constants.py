from net.packets.opcodes import CSendOps

HOST_IP = "127.0.0.1"
CENTER_PORT = 8383
LOGIN_PORT = 8484
GAME_PORT = 8585
SHOP_PORT = 8787

SECRET_KEY = 'Super Secret Key -- !'

WORLD_COUNT = 1
CHANNEL_COUNT = 1

VERSION = 95
SUB_VERSION = "1"
LOCALE = 8

EXP_RATE = 1
QUEST_EXP = 1
PARTY_QUEST_EXP = 1
MESO_RATE = 1
DROP_RATE = 1

LOG_PACKETS = True

AUTO_REGISDTER = True
REQUEST_PIN = False
REQUEST_PIC = False
REQUIRE_STAFF_IP = False
MAX_CHARACTERS = 3

DEFAULT_EVENT_MESSAGE = ""
DEFAULT_TICKER = "Welcome"
ALLOW_MULTI_LEVELING = False
DEFAULT_CREATION_SLOTS = 3
DISABLE_CHARACTER_CREATION = False


def filter_send_ops(send_op):
    if not LOG_PACKETS:
        return False
    
    # if send_op in [opcodes.]