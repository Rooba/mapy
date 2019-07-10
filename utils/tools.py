from asyncio import sleep

def splitNumber (num):
    lst = []
    while num > 0:
        lst.append(num & 0xFF)
        num >>= 8
    return lst[::-1]

def to_string(bytes_):
    return ' '.join([bytes_.hex()[i:i+2].upper() for i in range(0, len(bytes_.hex()), 2)])

async def wakeup():
    while True:
        await sleep(1)