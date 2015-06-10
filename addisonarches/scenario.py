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

from collections import Counter
from collections import namedtuple
import datetime
from decimal import Decimal
from enum import Enum
import random
import uuid

from addisonarches.business import Asset
from addisonarches.business import Business
from addisonarches.compound import Compound
from addisonarches.compound import Memory
from addisonarches.inventory import Volume
from addisonarches.valuation import ValueBook

from tallywallet.common.finance import Note

class Buying(Memory):
    pass

class Selling(Memory):
    pass

class Length(Enum):
    metre = 1

Commodity = namedtuple("Commodity", ["label", "description", "volume"])
Plank = namedtuple("Plank", Commodity._fields)
Table = namedtuple("Table", Commodity._fields)

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
    A shipment of tables from the Far East.
    """

    @staticmethod
    def recipe():
        return {Table: 10, Pallet: 1}

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

class HouseClearance(Business):
    """
    {proprietor.name} sells second-hand household articles. People
    come to him for desks and tables, which he doesn't always have,
    so he'd like to source cheap flat-pack ones also.

    """

    def __call__(self, loop=None):
        pass

class Hobbyist(Business):
    """
    {proprietor.name} breeds rabbits. He'll pay money for wooden
    pallets which he breaks down to build hutches.

    """

    def __call__(self, loop=None):
        pass

class Wholesale(Business):
    """
    {proprietor.name} sells manufactured goods wholesale in quantity.

    """

    def __call__(self, game, loop=None):
        try:
            focus = game.drama.memory[0]
        except (AttributeError, IndexError):
            greeting = random.choice(
                ["Hello, {0.name}".format(
                    game.businesses[0].proprietor
                ), "What can I do for you?"]
            )
            print("{0.name} says, '{1}'.".format(
                    self.proprietor, greeting
                 )
            )
        if isinstance(game.drama, Buying):
            try:
                offer = game.drama.memory[-1]
                if not self.book.approve(self.book[focus], offer):
                    valuation = self.book.consider(
                        focus, offer, constraint=0
                    )
                    print(
                        "'I can go to "
                        "{0.currency}{0.value:.0f}'.".format(valuation)
                    )
                else:
                    print(
                        "'I'll agree on "
                        "{0.currency}{0.value}'.".format(offer)
                    )
                    asset = Asset(focus, None, game.ts)
                    picks = self.retrieve(asset)
                    quantity = sum(i[1] for i in picks)
                    price = quantity * offer.value
                    game.businesses[0].store(
                        Asset(focus, quantity, game.ts)
                    )
                    game.drama = None
            except (TypeError, NotImplementedError) as e:
                print(e)
                # No offer yet
                print(
                    "{0.name} says, 'I see you're "
                    "considering this fine {1.label}'.".format(
                        self.proprietor, focus
                     )
                )
                print(
                    "'We let those go for "
                    "{0.currency}{0.value:.0f}'.".format(
                        max(self.book[focus])
                    )
                )
            except Exception as e:
                print(e)

class Recycling(Business):
    """
    {proprietor.name} runs a scrap metal yard. She always needs
    Swarfega and blue roll. She has a limited capacity for storing
    recovered fuel; she will consider selling petrol or diesel to
    you if she trusts you.

    """

    def __call__(self, loop=None):
        pass

class MarketStall(Business):
    """
    {proprietor.name} has a stall on the market. He'll buy anything
    but only at a rock-bottom price.

    """

    def __call__(self, loop=None):
        pass

class Antiques(Business):
    """
    {proprietor.name} runs an antique shop. She's always looking
    for fabrics which she cuts up and sells as rare designs. She'll
    also buy picture frames if they're cheap and contemporary.

    """

    def __call__(self, loop=None):
        pass

then = datetime.date(1985, 9, 4)
businesses = [
    HouseClearance(characters[0], ValueBook(), [locations[1]]),
    Wholesale(characters[3], ValueBook(), [locations[2]]).deposit(
        locations[2].name,
        ShipmentOfTables.build(Counter({
            Table("Table", "self-assembly dining", Volume.slab): 10,
            Pallet.build(Counter({
                Plank("Plank", "rough-cut softwood", Volume.slab): 6,
            })): 1,
        })),
        3,
        Note(
            date=then,
            principal=200,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
    ),
    Hobbyist(characters[7], ValueBook(), [locations[3]]).deposit(
        locations[3].name,
        Pallet.build(Counter({
            Plank("Plank", "rough-cut softwood", Volume.slab): 6,
        })),
        12
    ),
    Recycling(characters[8], ValueBook(), [locations[4]]),
    MarketStall(characters[10], ValueBook(), [locations[5]]),
    Antiques(characters[12], ValueBook(), [locations[6]]),
]

