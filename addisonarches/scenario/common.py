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
import uuid

from addisonarches.scenario.types import Character
from addisonarches.scenario.types import FormB107
from addisonarches.scenario.types import Keys
from addisonarches.scenario.types import Location
from addisonarches.scenario.types import Prisoner
from addisonarches.scenario.types import PrisonOfficer
from addisonarches.scenario.types import PrisonVisitor

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

ensemble = {
    Prisoner(id=uuid.uuid4().hex, name="Mr Martin Sheppey"),
    PrisonOfficer(id=uuid.uuid4().hex, name="Mr Ray Farington"),
    PrisonVisitor(id=uuid.uuid4().hex, name="Mrs Karen Sheppey"),
    FormB107(id=uuid.uuid4().hex),
    Keys(id=uuid.uuid4().hex, label="Addison Arches 18A"),
}

locations = [
    Location("Addison Arches 18a", 100),
    Location("Harry's House Clearances", 300),
    Location("Kinh Ship Bulk Buy", 500),
    Location("The Goldhawk Tavern", 10),
    Location("White City Non-ferrous Recovery Ltd.", 1000),
    Location("Indigent St. Open Market", 1000),
    Location("Itta's Antiques", 30),
    Location("HM Prison Pentonville, J Wing", None),
]

blue_monday = datetime.date(1978, 1, 16)
