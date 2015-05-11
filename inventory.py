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

from scenario import Commodity

Asset = namedtuple(
    "Asset",
    ["commodity", "quantity", "acquired"]
)
Offer = namedtuple("Offer", ["ts", "value", "currency"])

class Inventory:

    def __init__(self, capacity):
        self.capacity = capacity
        self.contents = Counter()

    @property
    def constraint(self) -> float:
        return sum(
            c.volume.value * n for c, n in self.contents.items()
        ) / self.capacity

class Business:

    def __init__(self, proprietor, locations, commodities):
        self.proprietor = proprietor
        self.locations = locations
        self.commodities = commodities

    def offer(self, commodity:Commodity, constraint=1.0):
        estimate = self.estimate(self[commodity])
        if offer.value > estimate.value or random.random() <= constraint:
            return self.commit(commodity, offer)
        else:
            return estimate

