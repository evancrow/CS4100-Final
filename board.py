from random import shuffle
from typing import Tuple, Dict, Optional

from tile import Tile
from edge import Edge
from intersection import Intersection
from location import Location

Coordinate = Tuple[int, int]

DEFAULT_TILE_RATIO = {
    Tile.Type.FOREST: 4,
    Tile.Type.PASTURE: 4,
    Tile.Type.GRAIN: 4,
    Tile.Type.ORE: 3,
    Tile.Type.BRICK: 3,
    Tile.Type.DESERT: 1,
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
        tiles = []

        for tile_type, roll in zip(tile_types, rolls):
            tiles.append(Tile(tile_type, roll))

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

        # Define vertex coordinates relative to a tile.
        vertex_offsets = [
            (0, 0, 0),
            (1, -1, 0),
            (1, 0, -1),
            (0, 1, -1),
            (-1, 1, 0),
            (-1, 0, 1)
        ]
        
        # Create intersections first.
        for tile_coord in grid.keys():
            q, r = tile_coord
            s = -q - r

            for i, (vq, vr, vs) in enumerate(vertex_offsets):
                vertex_coord = (q + vq/3, r + vr/3, s + vs/3)
                vertex_key = (vertex_coord[0], vertex_coord[1])
                location = Location.intersection(vertex_key[0], vertex_key[1])
                
                if location not in intersections:
                    adjacent_tiles = []
                    for adj_q, adj_r in grid.keys():
                        adj_s = -adj_q - adj_r
                        # Check if this tile is adjacent to the vertex.
                        for vq2, vr2, vs2 in vertex_offsets:
                            if (adj_q + vq2/3, adj_r + vr2/3, adj_s + vs2/3) == vertex_coord:
                                adjacent_tiles.append(grid[(adj_q, adj_r)])
                                break
                    
                    intersections[location] = Intersection(adjacent_tiles)
        
        # Now connect intersections and create edges.
        for tile_coord in grid.keys():
            q, r = tile_coord

            for i in range(6):
                v1_offset = vertex_offsets[i]
                v2_offset = vertex_offsets[(i + 1) % 6]
                
                v1_coord = (q + v1_offset[0]/3, r + v1_offset[1]/3)
                v2_coord = (q + v2_offset[0]/3, r + v2_offset[1]/3)
                
                location1 = Location.intersection(v1_coord[0], v1_coord[1])
                location2 = Location.intersection(v2_coord[0], v2_coord[1])
                edge_location = Location.edge(location1.coords, location2.coords)
                
                if edge_location not in edges:
                    edge = Edge(intersections[location1], intersections[location2])
                    edges[edge_location] = edge

                    intersections[location1].add_intersection(intersections[location2])
                    intersections[location2].add_intersection(intersections[location1])

        return Board(grid, edges, intersections)