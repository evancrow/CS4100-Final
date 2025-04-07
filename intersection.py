from uuid import uuid4
from typing import List

from player import Player
from structure import Structure
from tile import Tile

class Intersection:
    def __init__(self, tiles: List[Tile], location=None):
        self.id = uuid4()
        self.structure = None
        self.adjacent_intersections: List['Intersection'] = []
        self.adjacent_tiles = tiles
        self.location = location

    def add_intersection(self, intersection: 'Intersection'):

        """
        Add an adjacent intersection to this intersection.
        
        :param intersection: The intersection to add.
        """
        self.adjacent_intersections.append(intersection)

    def can_upgrade_to_city(self, player: Player) -> bool:
        """
        Check if the player can upgrade a settlement to a city at this intersection.
        
        :param player: The player who wants to upgrade.
        :return: True if the player can upgrade to a city, False otherwise.
        """
        # Must be a settlement owned by the player.
        return (self.structure is not None and 
                self.structure.owner == player and 
                self.structure.type == Structure.Type.SETTLEMENT)

    def build_structure(self, structure_type: Structure.Type, player: Player) -> Structure:
        """
        Build a structure at this intersection.
        
        :param structure_type: The type of structure to build.
        :param player: The player building the structure.
        :return: The built structure.
        """
        if structure_type == Structure.Type.SETTLEMENT:
            assert self.structure is None, "Cannot build settlement here"
        elif structure_type == Structure.Type.CITY:
            assert self.can_upgrade_to_city(player), "Cannot upgrade to city here"
        
        assert structure_type != Structure.Type.ROAD, "Cannot build roads at intersections"
        
        self.structure = Structure(structure_type, player)
        return self.structure