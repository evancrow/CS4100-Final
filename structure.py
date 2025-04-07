from enum import Enum
from uuid import uuid4

from tile import Tile

class Structure:
    class Type(Enum):
        ROAD = "Road"
        SETTLEMENT = "Settlement"
        CITY = "City"

        def required_cards(self):
            if self == Structure.Type.ROAD:
                return {Tile.Type.BRICK: 1, Tile.Type.FOREST: 1}
            elif self == Structure.Type.SETTLEMENT:
                return {Tile.Type.BRICK: 1, Tile.Type.FOREST: 1, Tile.Type.GRAIN: 1, Tile.Type.PASTURE: 1}
            elif self == Structure.Type.CITY:
                return {Tile.Type.GRAIN: 2, Tile.Type.ORE: 3}
            return {}

    def __init__(self, tile_type: Type, owner):
        self.id = uuid4()
        self.type = tile_type
        self.owner = owner