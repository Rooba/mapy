HOST_IP = "127.0.0.1"
CENTER_PORT = 8383
LOGIN_PORT = 8484
GAME_PORT = 8585
# if there are 20 worlds with 20 channels they will collide with 8787, future thought
SHOP_PORT = 8787

USE_DATABASE = False
DSN = "postgres://user:password@host:port/database?option=value"
DB_HOST = ""
DB_PASS = ""

USE_HTTP_API = True
HTTP_API_ROUTE = "http://127.0.0.1:54545"

CENTER_KEY = 'Super Secret Key -- !'

WORLD_COUNT = 1
CHANNEL_COUNT = 2

VERSION = 95
SUB_VERSION = "1"
LOCALE = 8

EXP_RATE = 1
QUEST_EXP = 1
PARTY_QUEST_EXP = 1
MESO_RATE = 1
DROP_RATE = 1

LOG_PACKETS = True

AUTO_LOGIN = False
AUTO_REGISDTER = True
REQUEST_PIN = False
REQUEST_PIC = False
REQUIRE_STAFF_IP = False
MAX_CHARACTERS = 3

DEFAULT_EVENT_MESSAGE = "Wow amazing world choose this one"
DEFAULT_TICKER = "Welcome"
ALLOW_MULTI_LEVELING = False
DEFAULT_CREATION_SLOTS = 3
DISABLE_CHARACTER_CREATION = False

PERMANENT = 150841440000000000

def get_job_from_creation(job_id):
    return {0: 3000, 1: 0, 2: 1000, 3: 2000, 4: 2001}.get(job_id, 0)