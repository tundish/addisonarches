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
import json
import logging
import operator
import os
import os.path
import pickle
from pprint import pprint
import sys
import tempfile
import time
import uuid

from turberfield.utils.expert import Expert
from turberfield.utils.expert import TypesEncoder

from addisonarches.business import CashBusiness
from addisonarches.scenario import Location
from addisonarches.scenario.types import Character


__doc__ = """
Encapsulates the game world in Addison Arches.
"""

class Persistent(Expert):

    Path = namedtuple("Path", ["root", "home", "slot", "file"])
    Pickled = namedtuple("Pickled", ["name", "path"])
    RSON = namedtuple("RSON", ["name", "attr", "path"])

    @staticmethod
    def make_path(path:Path, prefix="tmp", suffix=""):
        dctry = os.path.join(path.root, path.home)
        os.makedirs(dctry, exist_ok=True)

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
            path.root, path.home, next((i[1] for i in stats), None), path.file)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def declare(self, data, loop=None):
        super().declare(data, loop)
        events = (i for i in self._services.values()
                   if isinstance(i, Persistent.RSON))
        for each in events:
            path = Persistent.make_path(
                Persistent.recent_slot(each.path)._replace(file=each.path.file)
            )
            fP = os.path.join(*path)
            with Expert.declaration(fP) as output:
                output.write(
                    "\n".join(json.dumps(
                        dict(_type=type(i).__name__, **vars(i)),
                        output, cls=TypesEncoder, indent=0
                        )
                        for i in data.get(each.attr, []))
                )
        pickles = (i for i in self._services.values()
                   if isinstance(i, Persistent.Pickled)
                   and data.get(i.name, False))
        for p in pickles:
            fP = os.path.join(*p.path)
            with open(fP, "wb") as fObj:
                pickle.dump(data[p.name], fObj, 4)


class Clock(Persistent):

    Tick = namedtuple("Tick", ["ts", "value"])

    @staticmethod
    def options(
        parent=os.path.expanduser(os.path.join("~", ".addisonarches"))
    ):
        # No need for HATEOAS until knockout.js
        return OrderedDict([
            ("tick", Expert.Event("tick")),
            ("running", Expert.Attribute("running")),
            ("sequence", Expert.Attribute("sequence")),
            ("value", Expert.Attribute("value")),
        ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interval = 30
        self.sequence = (
            t for t in (
                datetime.datetime(year=2015, month=5, day=11) +
                datetime.timedelta(seconds=i)
                for i in itertools.islice(
                    itertools.count(0, 30 * 60),
                    7 * 24 * 60 // 30)
                )
            if 8 <= t.hour <= 19)
        self.stop = False

    @asyncio.coroutine
    def __call__(self, loop=None):
        val = next(self.sequence)
        while True:
            self.declare(
                dict(
                    tick=False,
                    value=val,
                    running=(not self.stop),
                    sequence=self.sequence
                ),
                loop=loop
            )

            if self.stop:
                break
            else:
                yield from asyncio.sleep(self.interval, loop=loop)

            try:
                ts = next(self.sequence)
            except StopIteration:
                self.stop = True
            finally:
                self.declare(
                    dict(
                        tick=True,
                        value=val,
                        running=(not self.stop),
                        sequence=self.sequence,
                    ),
                    loop=loop
                )


class Game(Persistent):

    Player = namedtuple("Player", ["user", "name"])
    Via = namedtuple("Via", ["id", "name", "tip"])

    @staticmethod
    def options(
        player,
        slot=None,
        parent=os.path.expanduser(os.path.join("~", ".addisonarches"))
    ):
        # No need for HATEOAS until knockout.js
        return OrderedDict([
            ("progress.rson", Persistent.RSON(
                "progress.rson",
                "progress",
                Persistent.Path(parent, player.user, slot, "progress.rson")
            )),
            ("businesses.pkl", Persistent.Pickled(
                "businesses",
                Persistent.Path(parent, player.user, slot, "businesses.pkl")
            )),
        ])

    def __init__(self, player, businesses, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player
        self.path = None
        self.businesses = businesses
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
            fP = os.path.join(*path)
            if not os.path.isfile(fP):
                proprietor = Character(uuid.uuid4().hex, self.player.name)
                locations = [Location("Addison Arches 18a", 100)]
                
                self.businesses.insert(
                    0, CashBusiness(proprietor, None, locations, tally=Decimal(1000)))
            else:
                with open(fP, "rb") as fObj:
                    self.businesses = pickle.load(fObj)

            self.path = path._replace(file=None)

        self.location = self.home
        return self

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
    def __call__(self, loop=None):
        while not Clock.public.running:
            yield from asyncio.sleep(0, loop=loop)

        while Clock.public.running:
            # TODO: refactor to a Clock class
            # 1. declare Locations
            #print("Here's where you can go:")
            #print(*["{0:01}: {1}".format(n, i)
            #        for n, i in enumerate(self.game.destinations)],
            #        sep="\n")
            #sys.stdout.write("\n")
            # 2. Declare splittables
            #   view = (
            #       (k, v)
            #       for k, v in self.game.here.inventories[
            #           self.game.location
            #       ].contents.items()
            #       if v and getattr(k, "components", None))
            progress = [
                Game.Via(n, i, None) for n, i in enumerate(self.destinations)
            ] + [
                Location(self.location, self.here.inventories[self.location].capacity),
                Clock.Tick(time.time(), Clock.public.value)
            ]
            self.declare(
                dict(
                    progress=progress,
                    businesses=self.businesses
                ),
                loop=loop
            )
            yield from Clock.public.tick.wait()

    @asyncio.coroutine
    def watch(self, q, **kwargs):
        loop = kwargs.pop("loop", None)
        msg = object()
        while msg is not None:
            msg = yield from q.get()
            if isinstance(msg, Game.Via):
                try: 
                    if self.destinations[msg.id] == msg.name:
                        # TODO: Advance clock?
                        self.location = msg.name
                        progress = [
                            Game.Via(n, i, None) for n, i in enumerate(self.destinations)
                        ] + [
                            Location(self.location, self.here.inventories[self.location].capacity),
                            Clock.Tick(time.time(), Clock.public.value)
                        ]
                        self.declare(dict(progress=progress))
                    else:
                        self._log.warning(msg)
                except Exception as e:
                    self._log.error(e)
