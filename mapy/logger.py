from re import I, X, compile
from sys import stdout
from threading import Lock

from loguru._logger import Core
from loguru._logger import Logger as _Logger, Level
from loguru._colorizer import Colorizer

from .constants import Worlds

PACKET_RE = compile(r"(?P<opcode>[\w\d._]+)\s(?P<ip>[\d.]+)\s(?P<packet>[A-Z\d\s]*)")
SERVER_RE = compile(
    r"""^
    (?P<server>
        (?P<name>[a-zA-Z]+\s?[a-zA-Z]+?)
        (?P<game>
            \[(?P<world_id>\d+)]
            \[(?P<ch_id>\d+)]
        )?
    )\s
    (?P<message>.+)$""",
    flags=I | X,
)


def pkt_fmt(bound):
    def _fmt_packet(rec):
        match_packet = PACKET_RE.search(rec["message"])
        if not match_packet:
            op_code, ip, packet = "Unknown" * 3
        else:
            op_code, ip, packet = list(match_packet.group(1, 2, 3))

        string = (
            f"<lg>[</lg><level>{bound}</level><lg>]</lg> "
            f"<r>[</r><level>{op_code}</level><r>]</r> "
            f"<g>[</g>{ip}<g>]</g> <w>{packet}</w>"
            "\n"
        )
        return string

    return _fmt_packet


def fmt_basic(record):
    owner = record["extra"]["owner"]
    lvl = record["level"].name.title()

    if owner.__class__.__name__ == "WvsGame":
        world_name = Worlds(owner.world_id).name.replace("_", " ").title()
        channel_id = owner.channel_id
        nam = f"{world_name}</ly>:<lr>{channel_id}"
        srv = f"<lg>[</lg><ly>{nam: <18}</lr><lg>]</lg> "
        name = f"{f'<lg>[</lg><level>{lvl}</level><lg>]</lg>': <41}" f"{srv: <47}"

    else:
        srv_name = owner.__class__.__name__
        name = (
            f"{f'<lg>[</lg><level>{lvl}</level><lg>]</lg>': <41}"
            f"{f'<lg>[</lg><lc>{srv_name: <9}</lc><lg>]</lg> ': <38}"
        )

    return f"{name}<level>{record['message']}</level>\n"


ipkt = Level("IN PACKET", 51, "<c>", None)
opkt = Level("OUT PACKET", 52, "<lm>", None)
basic = Level("BASIC", 11, "<lc>", None)


class Logger(_Logger):
    __core = Core()
    __pre_init__ = False
    __init_lock__ = Lock()

    with __core.lock:
        for v in [ipkt, opkt, basic]:
            __core.levels[v.name] = v
            __core.levels_ansi_codes[v.name] = Colorizer.ansify(v.color)
            for handler in __core.handlers.values():
                handler.update_format(v.name)

    def __init__(self, owner):
        super().__init__(
            self.__core,
            None,
            0,
            False,
            False,
            False,
            False,
            True,
            None,
            {"owner": owner},
        )

        with Logger.__init_lock__:
            if not Logger.__pre_init__:
                self.add(
                    stdout, level=ipkt.no, colorize=True, format=pkt_fmt("IN PACKET")
                )
                self.add(
                    stdout, level=opkt.no, colorize=True, format=pkt_fmt("OUT PACKET")
                )
                self.add(
                    stdout,
                    level=basic.no,
                    format=fmt_basic,
                    colorize=True,
                    diagnose=True,
                )
                Logger.__pre_init__ = True

    def log_ipkt(self, message):
        return self._log(ipkt.name, ipkt.no, False, self._options, message, (), {})

    def log_opkt(self, message):
        return self._log(opkt.name, opkt.no, False, self._options, message, (), {})

    def log_basic(self, message):
        return self._log(basic.name, basic.no, False, self._options, message, (), {})
