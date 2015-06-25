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
import random
import re

from addisonarches.business import Asset
from addisonarches.business import Business
from addisonarches.business import CashBusiness
from addisonarches.compound import Compound
from addisonarches.compound import Memory


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

class HouseClearance(CashBusiness):
    """
    {proprietor.name} sells second-hand household articles. People
    come to him for desks and tables, which he doesn't always have,
    so he'd like to source cheap flat-pack ones also.

    """

    def __call__(self, loop=None):
        pass

class Hobbyist(CashBusiness):
    """
    {proprietor.name} breeds rabbits. He'll pay money for wooden
    pallets which he breaks down to build hutches.

    """

    @staticmethod
    @Business.handler.register(Selling)
    def handle_selling(drama:Selling, self:Business, game):
        focus = drama.memory[0]
        try:
            valuations = self.book[type(focus)]
            offer = drama.memory[-1]
        except KeyError:
            # Not in book
            print(
                "{0.name} says, 'No thanks, "
                "not at the moment'.".format(
                    self.proprietor, focus
                 )
            )
            try:
                pick = random.choice(list(self.book.keys()))
                need = " ".join(i.lower() for i in re.split(
                "([A-Z][^A-Z]*)", pick.__name__) if i)
            except IndexError:
                print("'Thanks for coming over, {0.name}. Bye!'".format(
                    game.businesses[0].proprietor
                )
            )
            else:
                print("'Got any {0}s?'".format(need))
            game.drama = None
        except Exception as e:
            print(e)
        else:
            try:
                if not self.book.approve(valuations, offer):
                    valuation = self.book.consider(
                        type(focus), offer, constraint=0
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
                    picks = game.businesses[0].retrieve(asset)
                    quantity = sum(i[1] for i in picks)
                    price = quantity * offer.value
                    self.store(
                        Asset(focus, quantity, game.ts)
                    )
                    self.tally -= price
                    game.businesses[0].tally += price
                    game.drama = None
            except (TypeError, NotImplementedError) as e:
                # No offer yet
                print(
                    "{0.name} says: 'How much are you asking for "
                    "a {1.label}?'".format(
                        self.proprietor, focus
                     )
                )

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
        Business.handler(game.drama, self, game)

class Wholesale(CashBusiness):
    """
    {proprietor.name} sells manufactured goods wholesale in quantity.

    """

    @staticmethod
    @Business.handler.register(Buying)
    def handle_buying(drama:Buying, self:Business, game):
        focus = drama.memory[0]
        try:
            offer = game.drama.memory[-1]
            if not self.book.approve(self.book[type(focus)], offer):
                valuation = self.book.consider(
                    type(focus), offer, constraint=0
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
                game.businesses[0].tally -= price
                self.tally += price
                game.drama = None
        except (TypeError, NotImplementedError) as e:
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
                    max(self.book[type(focus)])
                )
            )
        except Exception as e:
            print(e)

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
        Business.handler(game.drama, self, game)

class Recycling(CashBusiness):
    """
    {proprietor.name} runs a scrap metal yard. She always needs
    Swarfega and blue roll. She has a limited capacity for storing
    recovered fuel; she will consider selling petrol or diesel to
    you if she trusts you.

    """

    def __call__(self, loop=None):
        pass

class MarketStall(CashBusiness):
    """
    {proprietor.name} has a stall on the market. He'll buy anything
    but only at a rock-bottom price.

    """

    def __call__(self, loop=None):
        pass

class Antiques(CashBusiness):
    """
    {proprietor.name} runs an antique shop. She's always looking
    for fabrics which she cuts up and sells as rare designs. She'll
    also buy picture frames if they're cheap and contemporary.

    """

    def __call__(self, loop=None):
        pass
