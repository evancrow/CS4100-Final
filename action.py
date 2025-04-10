from dataclasses import dataclass

from location import Location
from structure import Structure

class Action:
    pass

@dataclass
class Build(Action):
    type: Structure.Type
    location: Location

@dataclass
class NoneAction(Action):
    pass