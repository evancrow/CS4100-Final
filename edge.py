from typing import Union
from uuid import uuid4

from intersection import Intersection
from player import Player
from structure import Structure

class Edge:
    def __init__(self, start: Intersection, end: Intersection, location=None):
        self.id = uuid4()
        self.road: Union[Structure, None] = None
        self.start = start
        self.end = end
        self.location = location

    def build(self, player: Player) -> Structure:
        """
        Build a road on this edge.
        
        :param player: The player building the road.
        :return: The built road structure.
        """
        assert self.road is None
        self.road = Structure(Structure.Type.ROAD, player)
        return self.road