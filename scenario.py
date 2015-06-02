#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

# This file is part of Addison Arches.
#
# Addison Arches is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Addison Arches is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Addison Arches.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
from enum import Enum
import uuid

from business import Business
from compound import Compound
from compound import Memory
from inventory import Volume


class Length(Enum):
    metre = 1

Commodity = namedtuple("Commodity", ["label", "description", "volume"])
Plank = namedtuple("Plank", Commodity._fields)

class Pallet(Compound):

    @staticmethod
    def recipe():
        return {Plank: 6}

class Hutch(Compound):

    @staticmethod
    def recipe():
        return {Plank: 8}

Character = namedtuple("Character", ["uuid", "name"])
Location = namedtuple("Location", ["name", "capacity"])

characters = [
    Character(uuid.uuid4().hex, i)
    for i in (
    "Harry McAllister",
    "Sally Paul",
    "David Man",
    "Jimmy Wei Zhang",
    "Rob Fairfield",
    "Mike Phillips",
    "Ian Thomas",
    "Barry Lattimer",
    "Siobhan Regan",
    "Freddie Mays",
    "Ali Khan",
    "Rashid Khan",
    "Itta Metz",
)]

locations = [
    Location("Addison Arches 18a", 100),
    Location("Harry's House Clearances", 300),
    Location("Kinh Ship Bulk Buy", 500),
    Location("The Goldhawk Tavern", 10),
    Location("White City Non-ferrous Recovery Ltd.", 1000),
    Location("Indigent St. Open Market", 1000),
    Location("Itta's Antiques", 30),
]

commodities = [
    Commodity("Desk", "Self-assembly beech effect office desk", Volume.box),
    Commodity("Desk", "Antique mahogany campaign desk", Volume.load),
    Commodity("Bricks", "Reclaimed London clay bricks", Volume.load),
    Commodity("Topsoil", "Finest growing medium from Norfolk", Volume.heap),
    Commodity("VCRs", "Betamax video cassette recorders", Volume.box),
    Commodity("PVRs", "Freeview HD recorders with dual HDMI", Volume.box),
]

operations = [
]

businesses = [
    (characters[0], [locations[1]]),
    (characters[2], [locations[2]]),
    (characters[8], [locations[4]]),
    (characters[10], [locations[5]]),
    (characters[12], [locations[6]]),
]

class HouseClearance(Business):
    """
    {proprietor.name} sells second-hand household articles. People
    come to him for desks and tables, which he doesn't always have,
    so he'd like to offer them cheap flat-pack ones instead.
    """

    def __call__(self, loop=None):
        pass

__doc__ = """
{characters[0].name} sells second-hand household articles. People
come to him for desks and tables, which he doesn't always have,
so he'd like to offer them cheap flat-pack ones instead.

{characters[7].name} breeds rabbits. He'll pay money for wooden pallets
which he breaks down to build hutches.

{characters[8].name} runs a scrap metal yard. She always needs Swarfega
and blue roll. She has a limited capacity for storing recovered fuel,
so she will sell petrol or diesel to you if she trusts you.

{characters[10].name} has a stall on the market. He'll buy anything but
only at a rock-bottom price.

{characters[12].name} runs an antique shop. She's always looking for
fabrics which she cuts up and sells as rare designs. She'll also buy
picture frames if they're cheap and contemporary.
""".format(characters=characters)

print(__doc__)

