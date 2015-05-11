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

class Volume(Enum):

    pallet = 4
    load = 2
    heap = 1
    cubic_metre = 1
    pile = 25e-2
    barrel = 128e-3
    keg = 64e-3
    sack = 32e-3
    case = 16e-3
    bundle = 8e-3
    box = 4e-3
    carton = 2e-3
    bottle = 1e-3
    litre = 1e-3
    pack = 5e-4

Business = namedtuple(
    "Business", 
    ["character", "roles", "locations", "commodities"]
)

class Role(Enum):

    player = 1
    npc = 2
    trader = 3
    predator = 4

Character = namedtuple("Character", ["uuid", "name"])
Location = namedtuple("Location", ["name", "capacity"])
Commodity = namedtuple("Commodity", ["label", "description", "volume"])

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
    Location("Indigent St. Open Market", 1000),
    Location("Harry's House Clearances", 300),
    Location("White City Non-ferrous Recovery Ltd.", 1000),
    Location("Kinh Ship Bulk Buy", 500),
    Location("Itta's Antiques", 30),
    Location("Addison Arches 18a", 100),
]

commodities = [
    Commodity("Bricks", "Reclaimed London clay bricks", Volume.load),
    Commodity("Topsoil", "Finest growing medium from Norfolk", Volume.heap),
    Commodity("VCRs", "Betamax video cassette recorders", Volume.box),
    Commodity("PVRs", "Freeview HD recorders with dual HDMI", Volume.box),
]
