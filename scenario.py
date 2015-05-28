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

from inventory import Commodity
from inventory import Volume


class Role(Enum):

    player = 1
    npc = 2
    trader = 3
    predator = 4

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

businesses = [
    (characters[0], [locations[1]]),
    (characters[2], [locations[2]]),
    (characters[8], [locations[4]]),
    (characters[10], [locations[5]]),
    (characters[12], [locations[6]]),
]

trade = [
    (businesses[0], [
        (commodities[0], 40, 0),
        (commodities[1], 600, 1),
    ]),
]
