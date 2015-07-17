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

import ast
import asyncio
from collections import OrderedDict
from collections import namedtuple
import datetime
from decimal import Decimal
import itertools
import logging
import operator
import os
import os.path
import pickle
from pprint import pprint
import sys
import tempfile
import uuid

from turberfield.utils.expert import Expert

from addisonarches.business import CashBusiness
from addisonarches.scenario import Location
from addisonarches.scenario.types import Character


__doc__ = """
Encapsulates the game world in Addison Arches.
"""

class Persistent(Expert):

    Path = namedtuple("Path", ["root", "home", "slot", "file"])
    Pickled = namedtuple("Pickled", ["name", "path"])

    @staticmethod
    def make_path(path:Path, prefix="tmp", suffix=""):
        dctry = os.path.join(path.root, path.home)
        try:
            os.mkdir(dctry)
        except FileExistsError:
            pass

        if path.slot is None and path.file is not None:
                slot = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dctry)
                return path._replace(slot=os.path.basename(slot))
        else:
            return path

    @staticmethod
    def recent_slot(path:Path):
        slots = [i for i in os.listdir(os.path.join(path.root, path.home))
                 if os.path.isdir(os.path.join(path.root, path.home, i))]
        stats = [(os.path.getmtime(os.path.join(path.root, path.home, fP)), fP)
                 for fP in slots]
        stats.sort(key=operator.itemgetter(0), reverse=True)
        return Persistent.Path(
            path.root, path.home, next((i[1] for i in stats), None), None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def declare(self, data, loop=None):
        super().declare(data, loop)
        pickles = (i for i in self._services.values()
                   if isinstance(i, Persistent.Pickled)
                   and data.get(i.name, False))
        for p in pickles:
            fP = os.path.join(*p.path)
            with open(fP, "wb") as fObj:
                pickle.dump(data[p.name], fObj, 4)


class Game(Persistent):

    Player = namedtuple("Player", ["user", "name"])

    @staticmethod
    def options(
        player,
        slot=None,
        parent=os.path.expanduser(os.path.join("~", ".addisonarches"))
    ):
        return OrderedDict([
            ("businesses.pkl", Persistent.Pickled(
                "businesses",
                Persistent.Path(parent, player.user, slot, "businesses.pkl")
            )),
        ])

    def __init__(self, player, businesses, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player
        self.businesses = businesses
        self.interval = 30
        self.stop = False
        self.clock = (
            t for t in (
                datetime.datetime(year=2015, month=5, day=11) +
                datetime.timedelta(seconds=i)
                for i in itertools.islice(
                    itertools.count(0, 30 * 60),
                    7 * 24 * 60 // 30)
                )
            if 8 <= t.hour <= 19)
        self.location = None
        self.drama = None
        self.ts = None

    def load(self):
        name, pickler = next(
            ((k, v) for k, v in self._services.items()
            if isinstance(v, Persistent.Pickled)
            and v.name == "businesses"),
            None
        )
        if pickler is not None:
            path = Persistent.make_path(
                Persistent.recent_slot(pickler.path)._replace(file=pickler.path.file)
            )
            self._services[name] = self._services[name]._replace(path=path)
            if not os.path.isfile(os.path.join(*path)):
                proprietor = Character(uuid.uuid4().hex, self.player.name)
                locations = [Location("Addison Arches 18a", 100)]
                
                self.businesses.insert(
                    0, CashBusiness(proprietor, None, locations, tally=Decimal(1000)))
            else:
                # TODO: load businesses from pickle file
                pass

        self.location = self.home

    @property
    def home(self):
        return list(self.businesses[0].inventories.keys())[0]

    @property
    def destinations(self):
        return [
            nearby for nearby in self.here.inventories
            if nearby != self.location
        ] or [self.home] if self.location != self.home else [
            list(b.inventories.keys())[0] for b in self.businesses[1:]
        ]

    @property
    def here(self):
        return next(
            (b for b in self.businesses
            if self.location in b.inventories),
            None
        )

    @asyncio.coroutine
    def __call__(self, commands, executor, loop=None):
        while not self.stop:
            yield from asyncio.sleep(self.interval)
            yield from commands.put("wait")
            sys.stdout.write("\n")
            sys.stdout.flush()
