from typing import Union
from uuid import uuid4

from board import Board
from intersection import Intersection
from location import Location
from player import Player
from structure import Structure

class Edge:
    def __init__(self, start: Intersection, end: Intersection, location=None):
        self.id = uuid4()
        self.road: Union[Structure, None] = None
        self.start = start
        self.end = end
        self.location = location

    def can_build_road(self, player: Player, board: Board) -> bool:
        """
        Check if a player can build a road on this edge.
        A player can build a road if:
        1. There is no road on this edge already.
        2. The player has a settlement or city at one of the connected intersections.
        3. The player has a road connected to this edge at one of the intersections.
        
        :param player: The player who wants to build a road.
        :param board: The current board.
        :return: True if the player can build a road, False otherwise.
        """
        if self.road is not None:
            return False

        all_connected = board.get_all_at_location(self.location)
        for item in all_connected:
           if item.owner == player:
               return True

        return False

    def build(self, player: Player) -> Structure:
        """
        Build a road on this edge.
        
        :param player: The player building the road.
        :return: The built road structure.
        """
        assert self.can_build_road(player), "Cannot build road here"
        self.road = Structure(Structure.Type.ROAD, player)
        return self.road