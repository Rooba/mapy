from mapy.net.packet import ByteBuffer


class MovePath:
    def __init__(self, x=0, y=0, foothold=0, position=0):
        self.x = x
        self.y = y
        self.foothold = foothold
        self.stance = position
        self.vx = None
        self.vy = None

    def decode_move_path(self, move_path):
        ipacket = ByteBuffer(move_path)

        self.x = ipacket.decode_short()
        self.y = ipacket.decode_short()
        self.vx = ipacket.decode_short()
        self.vy = ipacket.decode_short()

        size = ipacket.decode_byte()

        for i in range(size):
            cmd = ipacket.decode_byte()

            if cmd == 0:
                self.x = ipacket.decode_short()
                self.y = ipacket.decode_short()
                xwob = ipacket.decode_short()
                ywob = ipacket.decode_short()
                self.foothold = ipacket.decode_short()
                xoff = ipacket.decode_short()
                yoff = ipacket.decode_short()
                self.stance = ipacket.decode_byte()
                duration = ipacket.decode_short()
            elif cmd == 1:
                xmod = ipacket.decode_short()
                ymod = ipacket.decode_short()
                self.stance = ipacket.decode_short()
                duration = ipacket.decode_short()
            elif cmd == 27:
                self.stance = ipacket.decode_byte()
                unk = ipacket.decode_short()
            else:
                break

    def __str__(self):
        return f"Position: {self.x},{self.y} - Foothold: {self.foothold} - Stance: {self.stance}"
