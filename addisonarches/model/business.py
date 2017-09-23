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
from collections import OrderedDict
import random
import re
import warnings

from addisonarches.model.compound import Memory
from addisonarches.model.inventory import Inventory

from turberfield.utils.assembly import Assembly


class Buying(Memory):
    pass

class Selling(Memory):
    pass

Asset = namedtuple(
    "Asset",
    ["commodity", "quantity", "acquired"]
)

class Handler:

    def handler(self, obj, *args, **kwargs):
        method = "_handle_{}".format(type(obj).__name__.lower())
        return getattr(self, method, None)

class Business:

    def __init__(self, proprietor, book, locations):
        self.proprietor = proprietor
        self.book = book
        self.inventories = OrderedDict([
            (i.name, Inventory(capacity=i.capacity))
             for i in locations])

    def deposit(self, locN, item, quantity, note=None):
        if self.inventories[locN].constraint > 1 or item is None:
            warnings.warn("Can't deposit {}".format(item))
            return item

        self.inventories[locN].contents[item] += quantity
        if note is not None:
            self.book.commit(type(item), note)
        return self

    def store(self, asset:Asset):
        rv = []
        unstored = asset.quantity
        schedule = iter(sorted(
            ((l.constraint, n, l) for n, l in self.inventories.items()),
            reverse=True))
        try:
            while unstored > 0:
                constraint, locN, loc = next(schedule)
                space = (1 - constraint) * loc.capacity
                vol = getattr(
                    asset.commodity.volume, "value", asset.commodity.volume
                )
                drop = min(
                    unstored, (space / vol) if vol else unstored
                )
                loc.contents[asset.commodity] += drop
                unstored -= drop
                rv.append((locN, drop))
        finally:
            return rv

    def retrieve(self, asset:Asset):
        rv = []
        schedule = iter(sorted(
            ((l.constraint, n, l) for n, l in self.inventories.items()),
            reverse=True))
        unfound = float("inf") if asset.quantity is None else asset.quantity
        try:
            while unfound > 0:
                constraint, locN, loc = next(schedule)
                pick = min(unfound, loc.contents[asset.commodity])
                loc.contents[asset.commodity] -= pick
                unfound -= pick
                rv.append((locN, pick))
        finally:
            return rv


class CashBusiness(Business):

    def __init__(self, *args, **kwargs):
        self.tally = kwargs.pop("tally", 0)
        super().__init__(*args, **kwargs)


class Trader(Handler, CashBusiness):

    Patter = namedtuple("Patter", ["actor", "text"])

    def _handle_buying(self, drama:Buying, game, ts=None):
        try:
            focus = drama.memory[0]
            offer = game.drama.memory[-1]
            if not self.book.approve(self.book[type(focus)], offer):
                valuation = self.book.consider(
                    type(focus), offer, constraint=0
                )
                yield Trader.Patter(self.proprietor, (
                    "I can go to "
                    "{0.currency}{0.value:.0f}.".format(valuation)
                ))
            else:
                yield Trader.Patter(self.proprietor, (
                    "We have a deal at "
                    "{0.currency}{0.value}.".format(offer)
                ))
                asset = Asset(focus, None, ts)
                picks = self.retrieve(asset)
                quantity = sum(i[1] for i in picks)
                price = quantity * offer.value
                game.businesses[0].store(
                    Asset(focus, quantity, ts)
                )
                game.businesses[0].tally -= price
                self.tally += price
                game.drama = None
                yield Trader.Patter(
                    self.proprietor,
                    "I'll have it all sent over."
                )
        except (TypeError, NotImplementedError) as e:
            # No offer yet
            yield Trader.Patter(self.proprietor, (
                "I see you're "
                "considering this fine {0.label}.".format(focus)
            ))
            yield Trader.Patter(self.proprietor, (
                "We let those go for "
                "{0.currency}{0.value:.0f}.".format(
                    max(self.book[type(focus)])
                )
            ))
        except Exception as e:
            print(e)
            yield(e)


    def _handle_selling(self, drama:Selling, game, ts=None):
        try:
            focus = drama.memory[0]
            valuations = self.book[type(focus)]
            offer = drama.memory[-1]
        except KeyError:
            # Not in book
            yield Trader.Patter(self.proprietor, "No thanks, not at the moment.")
            try:
                pick = random.choice(list(self.book.keys()))
                need = " ".join(i.lower() for i in re.split(
                "([A-Z][^A-Z]*)", pick.__name__) if i)
            except IndexError:
                yield Trader.Patter(
                    self.proprietor,
                    "Thanks for coming over, {0.name}. Bye!".format(
                        game.businesses[0].proprietor
                    )
                )
            else:
                yield Trader.Patter(self.proprietor, "Got any {0}s?".format(need))
            game.drama = None
        except Exception as e:
            yield(e)
        else:
            try:
                if not self.book.approve(valuations, offer):
                    valuation = self.book.consider(
                        type(focus), offer, constraint=0
                    )
                    yield Trader.Patter(self.proprietor, (
                        "I can go to "
                        "{0.currency}{0.value:.0f}.".format(valuation)
                    ))
                else:
                    yield Trader.Patter(self.proprietor, (
                        "I'll agree on "
                        "{0.currency}{0.value}.".format(offer)
                    ))
                    asset = Asset(focus, None, ts)
                    picks = game.businesses[0].retrieve(asset)
                    quantity = sum(i[1] for i in picks)
                    price = quantity * offer.value
                    self.store(
                        Asset(focus, quantity, ts)
                    )
                    self.tally -= price
                    game.businesses[0].tally += price
                    game.drama = None
            except (TypeError, NotImplementedError) as e:
                # No offer yet
                yield Trader.Patter(
                    self.proprietor,
                    "How much are you asking for a {0.label}?".format(focus)
                )

Assembly.register(Buying, Selling, Trader.Patter)
