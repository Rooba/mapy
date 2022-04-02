from re import IGNORECASE, compile, X
from .common.enum import Worlds

PACKET_RE = compile(
    r"(?P<opcode>[A-Za-z0-9\._]+)\s(?P<ip>[0-9\.]+)\s(?P<packet>[A-Z0-9\s]*)")

SERVER_RE = compile(
    r"""^
    (?P<server>
        (?P<name>[a-zA-Z]+\s?[a-zA-Z]+?)
        (?P<game>
            \[(?P<world_id>[0-9]+)\]
            \[(?P<ch_id>[0-9]+)\]
        )?
    )\s
    (?P<message>.+)$""",
    flags=IGNORECASE | X,
)

try:
    from loguru._logger import Logger as _Logger, Core
    from sys import stdout

    def fmt_packet(rec):
        direction = in_ if rec["level"].name == (in_ :=
                                                 "INPACKET") else "OUTPACKET"
        match_packet = PACKET_RE.search(rec["message"])
        op_code, ip, packet = list(match_packet.group(1, 2, 3))
        string = (f"<lg>[</lg><level>{direction:^12}</level><lg>]</lg> "
                  f"<r>[</r><level>{op_code}</level><r>]</r> "
                  f"<g>[</g>{ip}<g>]</g> <w>{packet}</w>"
                  "\n")
        return string

    def fmt_record(record):
        name, message = "Unnamed", ""
        if grps := getattr(SERVER_RE.search(record["message"]), "group", None):
            message = grps("message")
            name = grps("name")
            if grps("game"):
                name = f"""{(
                    f"<lc>{Worlds(int(grps('world_id'))).name}"
                    f"</lc>: <lr>{int(grps('ch_id')) + 1}</lr>"): <33}"""

        return ("<lg>[</lg>"
                f"<level>{record['level']: ^10}</level>"
                "<lg>]</lg>"
                f"<lg>[</lg>{name: <15}<lg>]</lg> "
                f"<level>{message}</level>"
                "\n")

    def filter_packets(record):
        return not record["level"] in ["INPACKET", "OUTPACKET"]

    class Logger(_Logger):

        def __init__(self):
            super().__init__(Core(), None, 0, False, False, False, False, True,
                             None, {})
            self.remove()
            self.level("INPACKET", no=50, color="<c>")
            self.level("OUTPACKET", no=50, color="<lm>")
            self.add(
                stdout,
                format=fmt_record,
                filter=filter_packets,
                colorize=True,
                diagnose=True,
            )
            self.add(
                stdout,
                level="INPACKET",
                colorize=True,
                format=fmt_packet,
            )
            self.add(
                stdout,
                level="OUTPACKET",
                colorize=True,
                format=fmt_packet,
            )

        def packet(self, message, direction):
            return self._log(direction.upper() + "PACKET", None, False,
                             self._options, message, {}, {})

        def i_packet(self, message):
            return self._log("INPACKET", None, False, self._options, message,
                             (), {})

        def o_packet(self, message):
            return self._log("OUTPACKET", None, False, self._options, message,
                             (), {})

    log = Logger()

except ImportError:
    from logging import getLogger

    log = getLogger()
