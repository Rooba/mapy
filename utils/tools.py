from asyncio import sleep

def splitNumber (num):
    lst = []
    while num > 0:
        lst.append(num & 0xFF)
        num >>= 8
    return lst[::-1]

def spacePacket(packet):
    return ' '.join([packet[i:i+2] for i in range(0, len(packet), 2)])

async def wakeup():
    while True:
        await sleep(1)