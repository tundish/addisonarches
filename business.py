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

from inventory import Asset
from inventory import Inventory


class Business:

    def __init__(self, proprietor, book, locations):
        self.proprietor = proprietor
        self.book = book
        self.inventories = {i.name: Inventory(capacity=i.capacity) for i in locations}

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
                drop = min(unstored, space / asset.commodity.volume.value)
                loc.contents[asset.commodity] += drop
                unstored -= drop
                rv.append((locN, drop))
        finally:
            return rv

    def retrieve(self, asset:Asset):
        rv = []
        unfound = asset.quantity
        schedule = iter(sorted(
            ((l.constraint, n, l) for n, l in self.inventories.items()),
            reverse=True))
        try:
            while unfound > 0:
                constraint, locN, loc = next(schedule)
                pick = min(unfound, loc.contents[asset.commodity])
                loc.contents[asset.commodity] -= pick
                unfound -= pick
                rv.append((locN, pick))
        finally:
            return rv
