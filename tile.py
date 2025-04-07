from enum import Enum
from uuid import uuid4

class Tile:
    class Type(Enum):
        FOREST = "Forest"
        PASTURE = "Pasture"
        GRAIN = "Grain"
        BRICK = "Brick"
        ORE = "Ore"
        DESERT = "Desert"

    def __init__(self, tile_type: Type, roll: int):
        self.id = uuid4()
        self.type = tile_type
        self.roll = roll
