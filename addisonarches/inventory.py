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
from enum import Enum


class Volume(Enum):

    pallet = 4
    load = 2
    heap = 1
    cubic_metre = 1
    pile = 25e-2
    box = 128e-3
    barrel = 128e-3
    keg = 64e-3
    sack = 32e-3
    slab = 24e-3
    case = 16e-3
    bundle = 8e-3
    tray = 4e-3
    carton = 2e-3
    brick = 1.5e-3
    bottle = 1e-3
    litre = 1e-3
    pack = 5e-4
    zero = 0


class Inventory:

    def __init__(self, capacity):
        self.capacity = capacity
        self.contents = Counter()

    @property
    def constraint(self) -> float:
        return sum(
            c.volume.value * n for c, n in self.contents.items()
        ) / self.capacity
