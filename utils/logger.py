from loguru import logger
from re import sub

def filter_packets(record): 
    return record['level'] not in ["INPACKET", "OUTPACKET"]

def filter_bound_out(record): 
    return record['level'] == "OUTPACKET"

def filter_bound_in(record):
    return record['level'] == "INPACKET"

def packet(message, bound): 
    return logger._log(bound.upper() + "PACKET", 50, message, (), {})

logger.packet = packet

def make_string(message):
    main_formatters = (
        ('r',  ( '\|', '\|')),
        ('lr', ( '\|', '&' )),
        ('c',  ( '~',  '~' )),
        ('lc', ( '~',  '&' )),
        ('y',  ( '#',  '#' )),
        ('ly', ('#',   '&' )),
        ('g',  ('\^', '\^' )),
        ('lg', ('\^',  '&' )),
        ('m',  ('@',   '@' )),
        ('lm', ('@',   '&' ))
        )
    replacers = ")[A-Za-z0-9\s]+(?P<tail>"

    i = 1
    for key, pair in main_formatters:
        replacers = pair[0] + replacers + pair[1]
        if len(main_formatters) > i:
            replacers = "|" + replacers + "|"
        else:
            break
        i += 1

    def ret(match):
        str_ = match.group('find')

        inner = match.group('inner_content') if match.group('inner_content') else ''
        outer = match.group('outer_content') if match.group('outer_content') else ''
        left = match.group('left_start') if match.group('left_start') else ''
        right = match.group('left_end') if match.group('left_end') else ''

        for key, pair in main_formatters:
            if match.group('head') == pair[0].strip('\\') and match.group('tail') == pair[1].strip('\\'):
                replace_str = match.group('find')[:].strip(pair[0].strip('\\') + pair[1].strip('\\'))
                str_ = f"<{key}>{replace_str}</{key}>"
        
        if left and not right:
            str_ = f"<level>{inner}</level> {str_} <level>"

        else:
            str_ = f"{left}{inner}{right}{outer}{str_} "

        return str_
    
    reg_str = f"\s?(?P<left_start><level>)?(?P<inner_content>[a-zA-Z0-9\s\[\]\_\-\.]+)?(?P<left_end></level>)?(?P<outer_content>[a-zA-Z0-9\s\[\]\_\-\.]+)?\-\-(?P<find>(?P<head>{replacers}))\s?"
    repl_str = sub(reg_str, ret, message)
    return repl_str