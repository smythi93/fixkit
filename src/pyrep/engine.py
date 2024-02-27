from pyrep.localization import Localization
from pyrep.repair import Repair


class Engine:
    def __init__(self, localization: Localization, repair: Repair):
        self.localization = localization
        self.repair = repair
