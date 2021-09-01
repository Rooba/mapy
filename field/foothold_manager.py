from math import atan, cos


class FootholdManager:
    def __init__(self):
        self.footholds = []

    def add(self, foothold):
        self.footholds.append(foothold)

    def find_below(self, tag_point):
        matches = []

        for foothold in self.footholds:
            if foothold.x1 <= tag_point.x and foothold.x2 >= tag_point.x:
                matches.append(foothold)

        for foothold in matches:
            if not foothold.wall and foothold.y1 != foothold.y2:
                s1 = foothold.y2 - foothold.y1
                s2 = foothold.x2 - foothold.x1
                s4 = tag_point.x - foothold.x1
                alpha = atan(s2 / s1)
                beta = atan(s1 / s2)
                s5 = cos(alpha) * (s4 / cos(beta))

                if foothold.y2 < foothold.y2:
                    calcy = foothold.y1 - int(s5)
                else:
                    calcy = foothold.y1 + int(s5)

                if calcy >= tag_point.y:
                    return foothold

            elif not foothold.wall and foothold.y1 >= tag_point.y:
                return foothold

        return None
