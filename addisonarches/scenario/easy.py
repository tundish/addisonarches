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
import datetime
from decimal import Decimal

from addisonarches.inventory import Volume
from addisonarches.scenario.common import blue_monday
from addisonarches.scenario.common import characters
from addisonarches.scenario.common import locations
from addisonarches.scenario.types import Antiques
from addisonarches.scenario.types import Commodity
from addisonarches.scenario.types import Hobbyist
from addisonarches.scenario.types import HouseClearance
from addisonarches.scenario.types import MarketStall
from addisonarches.scenario.types import Pallet
from addisonarches.scenario.types import Plank
from addisonarches.scenario.types import Recycling
from addisonarches.scenario.types import ShipmentOfTables
from addisonarches.scenario.types import Table
from addisonarches.scenario.types import Wholesale
from addisonarches.valuation import ValueBook

from tallywallet.common.finance import Note

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
            date=blue_monday,
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
        12,
        Note(
            date=blue_monday,
            principal=7,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
    ),
    Recycling(characters[8], ValueBook(), [locations[4]]),
    MarketStall(characters[10], ValueBook(), [locations[5]]),
    Antiques(characters[12], ValueBook(), [locations[6]]),
]

