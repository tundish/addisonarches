import enum

from turberfield.dialogue.types import EnumFactory
from turberfield.utils.assembly import Assembly

class Location(EnumFactory, enum.Enum):
    foyer = 0
    bar = 1
    cloakroom_floor = 2
    cloakroom_space = 3
    cloakroom_hook = 4

