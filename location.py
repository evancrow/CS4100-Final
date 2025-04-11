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

    def distance_to(self, other: 'Location') -> float:
        if self.is_intersection() and other.is_intersection():
            q1, r1 = self.coords
            q2, r2 = other.coords

            return max(abs(q1 - q2), abs(r1 - r2), abs(q1 + r1 - q2 - r2))
        elif self.is_edge() and other.is_edge():
            (a1, a2), (b1, b2) = self.coords
            (c1, c2), (d1, d2) = other.coords

            dist1 = max(abs(a1 - c1), abs(a2 - c2), abs(a1 + a2 - c1 - c2))
            dist2 = max(abs(a1 - d1), abs(a2 - d2), abs(a1 + a2 - d1 - d2))
            dist3 = max(abs(b1 - c1), abs(b2 - c2), abs(b1 + b2 - c1 - c2))
            dist4 = max(abs(b1 - d1), abs(b2 - d2), abs(b1 + b2 - d1 - d2))
            
            return min(dist1, dist2, dist3, dist4)