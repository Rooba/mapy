from loguru import logger
from re import IGNORECASE, compile, X
from sys import stdout


SERVER_PATTERN = compile(
    r"""^
    (?P<server>
        (?P<name>LoginServer|GameServer)
        (?P<game>
            \((?P<world_id>[0-9]+)\)
            \((?P<channel_id>[0-9]+)\)
        )?
    )\s
    (?P<message>.+)$""",
    flags=IGNORECASE | X,
)
SERVER_FN = lambda match: (
    "<r>[</r>"
    f"<w>{match.group('name')}"
    f"(<ly>{match.group('world_id')}</ly>)"
    f"(<lg>{match.group('channel_id')}</lg>)"
    "</w><r>]</r>"
)


def filter_packets(record):
    return record["level"] not in ["INPACKET", "OUTPACKET"]


def filter_bound(direction):
    def wrap(record):
        return record["level"] == direction

    return wrap


def packet(message, bound):
    return logger._log(
        bound.upper() + "PACKET", 50, False, logger._options, message, (), {}
    )


setattr(logger, "packet", packet)
logger.remove()


def setup_logger():
    def main_formatter(record):
        match = SERVER_PATTERN.search(record["message"])

        if match:
            if match.group("game"):
                message = match.group("message")
                server_name = (
                    "<r>[</r>"
                    f"<w>{match.group('name')}"
                    f"(<ly>{match.group('world_id')}</ly>)"
                    f"(<lg>{match.group('channel_id')}</lg>)"
                    "</w><r>]</r>"
                )

            else:
                message = match.group("message")
                server_name = f"<r>[</r><w>{match.group('name')}</w><r>]</r>"

        else:
            server_name = "<r>[</r>ServerApp<r>]</r>"
            message = record["message"]

        string = (
            f"<lg>[</lg><level>{record['level']:^12}</level><lg>]</lg>"
            f" {server_name} <level>{message}</level>"
        )
        return string + "\n"

    logger.add(
        stdout,
        filter=filter_packets,
        colorize=True,
        format=main_formatter,
        diagnose=True,
    )

    def packet_fmt(direction):
        packet_re = compile(
            r"(?P<opcode>[A-Za-z0-9\._]+)\s(?P<ip>[0-9\.]+)\s(?P<packet>[A-Z0-9\s]*)"
        )

        def wrap(record):
            match_packet = packet_re.search(record["message"])
            matches = list(match_packet.group(1, 2, 3))
            string = (
                f"<lg>[</lg><level>{direction:^12}</level><lg>]</lg> "
                f"<r>[</r><level>{matches[0]}</level><r>]</r> "
                f"<g>[</g>{matches[1]}<g>]</g> <w>{matches[2]}</w>"
                "\n"
            )
            return string

        return wrap

    logger.level("INPACKET", 0, color="<c>")
    logger.level("OUTPACKET", 0, color="<lm>")
    logger.add(
        stdout,
        colorize=True,
        level="INPACKET",
        filter=filter_bound("INPACKET"),
        format=packet_fmt("INPACKET"),
    )
    logger.add(
        stdout,
        colorize=True,
        level="OUTPACKET",
        filter=filter_bound("OUTPACKET"),
        format=packet_fmt("OUTPACKET"),
    )


# def make_string(message):
# main_formatters = (
#     ('r',  ( r'\|', r'\|')),
#     ('lr', ( r'\|', '&' )),
#     ('c',  ( '~',  '~' )),
#     ('lc', ( '~',  '&' )),
#     ('y',  ( '#',  '#' )),
#     ('ly', ('#',   '&' )),
#     ('g',  (r'\^', r'\^' )),
#     ('lg', (r'\^',  '&' )),
#     ('m',  ('@',   '@' )),
#     ('lm', ('@',   '&' ))
#     )
# replacers = r")[A-Za-z0-9\s]+(?P<tail>"

# i = 1
# for _, pair in main_formatters:
#     replacers = pair[0] + replacers + pair[1]
#     if len(main_formatters) > i:
#         replacers = "|" + replacers + "|"
#     else:
#         break
#     i += 1

# def ret(match):
#     str_ = match.group('find')

#     inner = match.group('inner_content') if match.group('inner_content') else ''
#     outer = match.group('outer_content') if match.group('outer_content') else ''
#     left = match.group('left_start') if match.group('left_start') else ''
#     right = match.group('left_end') if match.group('left_end') else ''

#     for key, pair in main_formatters:
#         if match.group('head') == pair[0].strip('\\') and match.group('tail') == pair[1].strip('\\'):
#             replace_str = match.group('find')[:].strip(pair[0].strip('\\') + pair[1].strip('\\'))
#             str_ = f"<{key}>{replace_str}</{key}>"

#     if left and not right:
#         str_ = f"<level>{inner}</level> {str_} <level>"

#     else:
#         str_ = f"{left}{inner}{right}{outer}{str_} "

#     return str_

# reg_str = fr"\s?(?P<left_start><level>)?(?P<inner_content>[a-zA-Z0-9\s\[\]\_\-\.]+)?(?P<left_end></level>)?(?P<outer_content>[a-zA-Z0-9\s\[\]\_\-\.]+)?\-\-(?P<find>(?P<head>{replacers}))\s?"
# repl_str = sub(reg_str, ret, message)
# return message

setup_logger()
