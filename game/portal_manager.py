from random import choice

class PortalManager:
    def __init__(self):
        self.portals = []
    
    def add(self, portal):
        self.portals.append(portal)

    def get_portal(self, name):
        return next((portal for portal in self.portals if portal.name == name), None)
    
    def get_random_spawn(self):
        portals = [portal for portal in self.portals if portal.name == 'sp']

        if not len(portals):
            return 0
        
        return choice(portals).id