from loguru import logger
from re import IGNORECASE, compile, X
from sys import stdout
from common.enum import Worlds


SERVER_PATTERN = compile(
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


def fmt_record(record):
    name, message = "Unnamed", ""
    if (grps := getattr(
            SERVER_PATTERN.search(record["message"]),
            "group",
            None)):
        message = grps("message")
        name = grps("name")
        if grps("game"):
            name = f"""{(
                f"<lc>{Worlds(int(grps('world_id'))).name}"
                f"</lc>: <lr>{int(grps('ch_id')) + 1}</lr>"): <33}"""

    return (
        "<lg>[</lg>"
        f"<level>{record['level']: ^10}</level>"
        "<lg>]</lg>"
        f"<lg>[</lg>{name: <15}<lg>]</lg> "
        f"<level>{message}</level>"
        "\n"
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


setattr(logger, "packet", packet)
logger.remove()


def setup_logger():
    logger.add(
        stdout,
        filter=filter_packets,
        colorize=True,
        format=fmt_record,
        diagnose=True,
        enqueue=True
    )

    logger.level("INPACKET", 0, color="<c>")
    logger.level("OUTPACKET", 0, color="<lm>")
    logger.add(
        stdout,
        colorize=True,
        level="INPACKET",
        filter=filter_bound("INPACKET"),
        format=packet_fmt("INPACKET"),
        diagnose=True,
        enqueue=True
    )
    logger.add(
        stdout,
        colorize=True,
        level="OUTPACKET",
        filter=filter_bound("OUTPACKET"),
        format=packet_fmt("OUTPACKET"),
        diagnose=True,
        enqueue=True
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
