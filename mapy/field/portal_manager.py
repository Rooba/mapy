from random import choice


class PortalManager:

    def __init__(self):
        self.portals = []

    def add(self, portal):
        self.portals.append(portal)

    def __filter_portals(self, name):
        return filter(lambda p: p.name == name, self.portals)

    def get_portal(self, name):
        return next(self.__filter_portals(name), None)

    def get_random_spawn(self):
        portals = list(self.__filter_portals("sp"))

        return choice(portals).id if portals else 0
