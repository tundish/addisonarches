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

from addisonarches.business import Trader
from addisonarches.compound import Compound

from turberfield.utils.assembly import Assembly


class Length(Enum):
    metre = 1

Commodity = namedtuple("Commodity", ["label", "description", "volume"])
Plank = namedtuple("Plank", Commodity._fields)
Table = namedtuple("Table", Commodity._fields)

class DataObject:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class Persona(DataObject):
    pass

class Prisoner(Persona): pass
class PrisonOfficer(Persona): pass
class PrisonVisitor(Persona): pass

class Pallet(Compound):

    @staticmethod
    def recipe():
        return {Plank: 6}

class Hutch(Compound):

    @staticmethod
    def recipe():
        return {Plank: 8}

class ShipmentOfTables(Compound):
    """
    from the Far East.
    """

    @staticmethod
    def recipe():
        return {Table: 10, Pallet: 1}


Character = namedtuple("Character", ["uuid", "name"])
Location = namedtuple("Location", ["name", "capacity"])

class HouseClearance(Trader):
    """
    {proprietor.name} sells second-hand household articles. People
    come to him for desks and tables, which he doesn't always have,
    so he'd like to source cheap flat-pack ones also.

    """
    pass

class Hobbyist(Trader):
    """
    {proprietor.name} breeds rabbits. He'll pay money for wooden
    pallets which he breaks down to build hutches.

    """
    pass

class Wholesale(Trader):
    """
    {proprietor.name} sells manufactured goods wholesale in quantity.

    """
    pass

class Recycling(Trader):
    """
    {proprietor.name} runs a scrap metal yard. She always needs
    Swarfega and blue roll. She has a limited capacity for storing
    recovered fuel; she will consider selling petrol or diesel to
    you if she trusts you.

    """
    pass

class MarketStall(Trader):
    """
    {proprietor.name} has a stall on the market. He'll buy anything
    but only at a rock-bottom price.

    """
    pass

class Antiques(Trader):
    """
    {proprietor.name} runs an antique shop. She's always looking
    for fabrics which she cuts up and sells as rare designs. She'll
    also buy picture frames if they're cheap and contemporary.

    """
    pass

Assembly.register(
    Character, Commodity, Location, Plank, Table
)
