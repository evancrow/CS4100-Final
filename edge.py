from uuid import uuid4

from intersection import Intersection
from player import Player
from structure import Structure

class Edge:
    def __init__(self, start: Intersection, end: Intersection):
        self.id = uuid4()
        self.road = None
        self.start = start
        self.end = end

    def can_build_road(self, player: Player) -> bool:
        """
        Check if a player can build a road on this edge.
        A player can build a road if:
        1. There is no road on this edge already
        2. The player has a settlement or city at one of the connected intersections
        3. The player has a road connected to this edge at one of the intersections
        
        :param player: The player who wants to build a road.
        :return: True if the player can build a road, False otherwise.
        """
        # Check if there's already a road on this edge
        if self.road is not None:
            return False

        # Check if player has a structure at either intersection
        if (self.start.structure is not None and self.start.structure.owner == player) or \
           (self.end.structure is not None and self.end.structure.owner == player):
            return True
            
        # Check if player has a connected road
        for adjacent_edge in self._get_adjacent_edges(player):
            if adjacent_edge is not None and adjacent_edge.road is not None and adjacent_edge.road.owner == player:
                return True

        return False
    
    def _get_adjacent_edges(self, player: Player):
        """
        Get edges that are adjacent to this edge (sharing an intersection).
        This is a helper method that would normally be used to check for connected roads.
        
        In a full implementation, this would need access to the board to find all adjacent edges.
        For now, this is a placeholder.
        
        :param player: The player to check connections for.
        :return: A list of adjacent edges.
        """
        # In a full implementation, this would return all edges connected to 
        # the start and end intersections of this edge
        return []

    def build(self, player: Player) -> Structure:
        """
        Build a road on this edge.
        
        :param player: The player building the road.
        :return: The built road structure.
        """
        assert self.can_build_road(player), "Cannot build road here"
        self.road = Structure(Structure.Type.ROAD, player)
        return self.road