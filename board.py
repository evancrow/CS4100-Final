import math
from random import shuffle
from typing import Tuple, Dict, Optional, Union

from constants import HEX_SIZE
from player import Player
from structure import Structure
from tile import Tile
from edge import Edge
from intersection import Intersection
from location import Location
from util import hex_to_pixel, snap

Coordinate = Tuple[int, int]

DEFAULT_TILE_RATIO = {
    Tile.Type.FOREST: 4,
    Tile.Type.PASTURE: 4,
    Tile.Type.GRAIN: 4,
    Tile.Type.ORE: 3,
    Tile.Type.BRICK: 3,
}

DEFAULT_ROLL_RATIOS = {
    2: 1,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    8: 2,
    9: 2,
    10: 2,
    11: 2,
    12: 1
}

class Board:
    def __init__(
        self,
        grid: Dict[Coordinate, Tile],
        edges: Dict[Location, Edge] = None,
        intersections: Dict[Location, Intersection] = None
    ):
        self.grid = grid
        self.edges = edges if edges is not None else {}
        self.intersections = intersections if intersections is not None else {}
    
    def get_structure_at_location(self, location: Location):
        """
        Get the structure at the given location.
        
        :param location: The location to check.
        :return: The structure at the location, or None.
        """
        if location.is_intersection():
            if location in self.intersections:
                return self.intersections[location].structure
        elif location.is_edge():
            if location in self.edges:
                return self.edges[location].road
        return None

    def get_all_at_location(self, location: Location) -> [Structure]:
        """
        Gets all the edges/intersections at the given location.
        For example:
        1. A structure.
        2. All the roads with at least one end touching the coord.

        :param location: The location to check.
        :return: All edges or intersections.
        """
        structures = []

        if location.is_intersection():
            intersection = self.get_at_location(location)
            if intersection:
                structures.append(intersection)

            for edge_loc, edge in self.edges.items():
                edge_start, edge_end = edge_loc.coords
                if edge_start == location.coords or edge_end == location.coords:
                    structures.append(edge)
                    
        elif location.is_edge():
            edge = self.get_at_location(location)
            if edge:
                structures.append(edge)

            start, end = location.coords
            start_intersection = self.get_all_at_location(Location.intersection(start[0], start[1]))
            end_intersection = self.get_all_at_location(Location.intersection(end[0], end[1]))
            
            if start_intersection:
                structures += start_intersection
            if end_intersection:
                structures += end_intersection
                
        return structures
    
    def get_at_location(self, location: Location) -> Optional[Edge or Intersection]:
        """
        Get the edge or intersection at the given location.
        
        :param location: The location to get.
        :return: The edge or intersection at the location, or None.
        """
        if location.is_intersection():
            return self.intersections.get(location)
        elif location.is_edge():
            return self.edges.get(location)
        return None

    def can_build_road(self, player: Player, edge: Edge) -> bool:
        """
        Check if a player can build a road on this edge.
        A player can build a road if:
        1. There is no road on this edge already.
        2. The player has a settlement or city at one of the connected intersections.
        3. The player has a road connected to this edge at one of the intersections.

        :param player: The player who wants to build a road.
        :param edge: The edge to check.
        :return: True if the player can build a road, False otherwise.
        """
        if edge.road is not None:
            return False

        all_connected = self.get_all_at_location(edge.location)
        for item in all_connected:
            if item.owner == player:
                return True

        return False

    def can_build_structure(self, player: Player, intersection: Intersection, initial_placement_rules: bool = False) -> bool:
        """
        Check if a structure can be built at this intersection.
        A player can build a structure if:
        1. There is no structure at this intersection.
        2. There are no structures at adjacent intersections.
        3. Player must have roads to the structure.

        :param player: The player who wants to build.
        :param intersection: The intersection to check.
        :param initial_placement_rules: True if rules are different for initial placing rules.
        :return: True if a structure can be built, False otherwise.
        """
        if intersection.structure is not None:
            return False

        # Check if there are any structures at adjacent intersections.
        for adj_intersection in intersection.adjacent_intersections:
            if adj_intersection.structure is not None:
                return False

        if initial_placement_rules:
            return True

        # Check that player has a road connecting directly to this intersection.
        if player and intersection.location:
            for edge_loc, edge in self.edges.items():
                edge_start, edge_end = edge_loc.coords
                if (edge_start == intersection.location.coords or edge_end == intersection.location.coords) and edge.road and edge.road.owner == player:
                    return True
                    
            return False

        return True

    @staticmethod
    def create_default_board():
        """
        Creates the default Catan board.
        :return: A type of Board with all the tiles, edges, and intersections.
        """
        # Create a list of all possible rolls and tiles.
        tile_types = []
        rolls = []

        for tile_type in DEFAULT_TILE_RATIO.keys():
            tile_types += [tile_type] * DEFAULT_TILE_RATIO[tile_type]

        for roll in DEFAULT_ROLL_RATIOS.keys():
            rolls += [roll] * DEFAULT_ROLL_RATIOS[roll]

        shuffle(tile_types)
        shuffle(rolls)

        # Combine the tiles and rolls.
        tiles = [Tile(Tile.Type.DESERT, 0)]

        for tile_type, roll in zip(tile_types, rolls):
            tiles.append(Tile(tile_type, roll))

        shuffle(tiles)

        index = 0
        grid = {}

        for q in range(-2, 3):
            for r in range(-2, 3):
                s = -q - r
                if -2 <= s <= 2:
                    grid[(q, r)] = tiles[index]
                    index += 1

        edges = {}
        intersections = {}

        # Build intersections.
        for (q, r), tile in grid.items():
            cx, cy = hex_to_pixel(q, r)

            corners_px = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = math.radians(angle_deg)
                corner_x = cx + HEX_SIZE * math.cos(angle_rad)
                corner_y = cy + HEX_SIZE * math.sin(angle_rad)
                location = Location.intersection(*snap(corner_x, corner_y))
                corners_px.append(location)

                if location not in intersections:
                    intersections[location] = Intersection([], location)

                if tile not in intersections[location].adjacent_tiles:
                    intersections[location].adjacent_tiles.append(tile)
        
            # Now connect intersections and create edges.
            for i in range(6):
                start = corners_px[i]
                end = corners_px[(i + 1) % 6]
                edge_loc = Location.edge(start.coords, end.coords)
                
                if edge_loc not in edges:
                    start_intersection = intersections[start]
                    end_intersection = intersections[end]
                    edge_obj = Edge(start_intersection, end_intersection, edge_loc)
                    edges[edge_loc] = edge_obj

                    start_intersection.add_intersection(end_intersection)
                    end_intersection.add_intersection(start_intersection)

        return Board(grid, edges, intersections)