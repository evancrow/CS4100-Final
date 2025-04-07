from enum import Enum
from typing import Tuple, Union, NamedTuple

class Location(NamedTuple):
    class Type(Enum):
        INTERSECTION = "Intersection"
        EDGE = "Edge"

    coords: Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]
    type: Type
    
    @staticmethod
    def intersection(q: float, r: float):
        return Location((q, r), Location.Type.INTERSECTION)
    
    @staticmethod
    def edge(coord1: Tuple[float, float], coord2: Tuple[float, float]):
        sorted_coords: Tuple[Tuple[float, float], Tuple[float, float]] = tuple(sorted([coord1, coord2]))
        return Location(sorted_coords, Location.Type.EDGE)
    
    def is_intersection(self) -> bool:
        return self.type == Location.Type.INTERSECTION
    
    def is_edge(self) -> bool:
        return self.type == Location.Type.EDGE