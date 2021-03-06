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
from collections import deque
from collections import OrderedDict
from collections import namedtuple
import datetime
from decimal import Decimal
import getpass
import itertools
import logging
import operator
import os
import os.path
import pickle
import random
import sys
import tempfile
import time
import uuid

from turberfield.dialogue.model import Model
from turberfield.dialogue.types import Player
from turberfield.dialogue.viewer import run_through
from turberfield.ipc.message import Alert
from turberfield.ipc.message import Message
from turberfield.ipc.message import parcel
from turberfield.ipc.message import reply
from turberfield.utils.assembly import Assembly
from turberfield.utils.expert import Expert
from turberfield.utils.misc import gather_installed

from addisonarches.business import Buying
from addisonarches.business import CashBusiness
from addisonarches.business import Selling
from addisonarches.business import Trader

import addisonarches.scenario.easy
import addisonarches.scenario.common
import addisonarches.scenario.icons
from addisonarches.scenario.common import blue_monday
from addisonarches.scenario.common import locations
from addisonarches.scenario.common import Location

from addisonarches.scenario.types import Commodity
from addisonarches.scenario.types import FormB107
from addisonarches.scenario.types import Keys
from addisonarches.scenario.types import Location
from addisonarches.scenario.types import Prisoner
from addisonarches.scenario.types import PrisonOfficer
from addisonarches.scenario.types import PrisonVisitor

from addisonarches.valuation import Ask
from addisonarches.valuation import Bid


__doc__ = """
Encapsulates the game world in Addison Arches.
"""

class Persistent(Expert):

    Path = namedtuple("Path", ["root", "home", "slot", "file"])
    Pickled = namedtuple("Pickled", ["name", "path"])
    RSON = namedtuple("RSON", ["name", "attr", "path"])

    @staticmethod
    def make_path(path:Path, prefix="tmp", suffix=""):
        if not path.home:
            path = path._replace(home=getpass.getuser())
        dctry = os.path.join(path.root, path.home)
        os.makedirs(dctry, exist_ok=True)

        if path.slot is None and path.file is not None:
                slot = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dctry)
                return path._replace(slot=os.path.basename(slot))
        else:
            return path

    @staticmethod
    def recent_slot(path:Path):
        try:
            slots = [i for i in os.listdir(os.path.join(path.root, path.home))
                     if os.path.isdir(os.path.join(path.root, path.home, i))]
            stats = [(os.path.getmtime(os.path.join(path.root, path.home, fP)), fP)
                     for fP in slots]
            stats.sort(key=operator.itemgetter(0), reverse=True)
        except:
            slots, stats = [], []
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
                for i in data.get(each.attr, []):
                    try:
                        Assembly.dump(i, output, indent=0)
                    except Exception as e:
                        self._log.error(". ".join(getattr(e, "args", e) or e))
                    finally:
                        output.write("\n")

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
            ("active", Expert.Event("active")),
            ("inactive", Expert.Event("inactive")),
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
        while True:
            yield from self.advance(loop)

            if self.stop:
                break
            else:
                yield from asyncio.sleep(self.interval, loop=loop)

    def advance(self, loop=None):
        try:
            val = next(self.sequence)
        except StopIteration:
            self.stop = True
        else:
            self.declare(
                dict(
                    active=True,
                    inactive=False,
                    value=val,
                    running=(not self.stop),
                    sequence=self.sequence,
                ),
                loop=loop
            )
            yield from asyncio.sleep(0, loop=loop)
            
            self.declare(
                dict(
                    active=False,
                    inactive=True,
                    value=val,
                    running=(not self.stop),
                    sequence=self.sequence,
                ),
                loop=loop
            )

class Game(Persistent):

    Avatar = namedtuple("Avatar", ["entity", "icon"])
    Drama = namedtuple("Drama", ["type", "mood"])
    Item = namedtuple("Item", ["type", "label", "description", "location", "owner"])
    Player = namedtuple("Player", ["user", "name"])
    Tally = namedtuple("Tally", ["actor", "name", "value", "units"])
    Via = namedtuple("Via", ["id", "name", "tip"])

    @staticmethod
    def options(
        player,
        slot=None,
        parent=os.path.expanduser(os.path.join("~", ".addisonarches"))
    ):
        # No need for HATEOAS until knockout.js
        return OrderedDict([
            ("diorama.rson", Persistent.RSON(
                "diorama.rson",
                "diorama",
                Persistent.Path(parent, player.user, slot, "diorama.rson")
            )),
            ("frame.rson", Persistent.RSON(
                "frame.rson",
                "frame",
                Persistent.Path(parent, player.user, slot, "frame.rson")
            )),
            ("inventory.rson", Persistent.RSON(
                "inventory.rson",
                "inventory",
                Persistent.Path(parent, player.user, slot, "inventory.rson")
            )),
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

    def __init__(self, player, businesses, clock=None, token=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player
        self.businesses = businesses
        self.clock = clock
        self.token = token

        # Network
        self.down = kwargs.pop("down", None)

        # Game state
        self.path = None
        self.location = None
        self.drama = None
        self.alerts = []
        self.dialogueQueue = None
        self.dialogue = deque(maxlen=4)
        self.shot = None
        self._log.info("Initialized.")

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
                proprietor = Player(id=uuid.uuid4().hex, name=self.player.name)
                locns = [Location("Addison Arches 18a", 100)]
                
                self.businesses.insert(
                    0, CashBusiness(proprietor, None, locns, tally=1000))
            else:
                with open(fP, "rb") as fObj:
                    self.businesses = pickle.load(fObj)

            self.path = path._replace(file=None)

        self.location = locations[-1].name
        return self

    @property
    def home(self):
        return list(self.businesses[0].inventories.keys())[0]

    @property
    def destinations(self):
        # TODO: separate Map expert
        return [self.home] if self.here is None else [
            nearby for nearby in self.here.inventories
            if nearby != self.location
        ] or [self.home] if self.location != self.home else [
            list(b.inventories.keys())[0] for b in self.businesses[1:]
        ]

    @property
    def here(self):
        # TODO: separate Map expert
        return next(
            (b for b in self.businesses
            if self.location in b.inventories),
            None
        )

    @property
    def inventory(self):
        capacity = self.here.inventories[self.location].capacity if self.here else None
        rv = [
            Game.Item("Compound", k.label, k.description, locn, 0)
            for locn, i in self.businesses[0].inventories.items()
            for k, v in i.contents.items()
            for n in range(v)
            if getattr(k, "components", None)
        ] + [
            Game.Item("Commodity", k.label, k.description, locn, 0)
            for locn, i in self.businesses[0].inventories.items()
            for k, v in i.contents.items()
            for n in range(v)
            if not getattr(k, "components", None)
        ]
        rv.append(
            Location(self.location, capacity)
        )
        return rv

    @property
    def diorama(self):
        """
        Ordered dictionary of entity: image asset

        """
        lookup = {i.name: i for i in addisonarches.scenario.icons.icons}
        return [a for a in (
            Game.Avatar(i, lookup.get(i.__class__.__name__.lower())) for i in self.ensemble)
            if a.icon is not None]

    @property
    def frame(self):
        return list(self.dialogue)

    @property
    def progress(self):
        capacity = self.here.inventories[self.location].capacity if self.here else None

        rv = [
            Clock.Tick(time.time(), Clock.public.value),
            Location(self.location, capacity),
            Game.Tally(None, "cash", self.businesses[0].tally, "\xa3"),
            Game.Drama(
                self.drama.__class__.__name__,
                self.drama.__class__.__name__.lower()
                if self.drama is not None
                else random.choice(
                    ["hopeful", "optimistic", "relaxed"]
                )
            )
        ] + [
            Game.Via(n, i, None) for n, i in enumerate(self.destinations)
        ]

        if self.here is not None:
            iBusiness = self.businesses.index(self.here)
            rv.extend([
                Game.Item("Compound", k.label, k.description, self.location, iBusiness) 
                for k, v in self.here.inventories[self.location].contents.items()
                for i in range(v)
                if getattr(k, "components", None)
            ])
            rv.extend([
                Game.Item("Commodity", k.label, k.description, self.location, iBusiness) 
                for k, v in self.here.inventories[self.location].contents.items()
                for i in range(v)
                if not getattr(k, "components", None)
            ])

            if self.here != self.businesses[0]:
                rv.append(self.here.proprietor)

            try:
                handler = self.here.handler(self.drama)
                reaction = handler(self.drama, self)
                rv.extend(list(reaction))
            except AttributeError:
                # Player business is not a Handler subclass
                self.alerts.append(Alert(
                    datetime.datetime.now(),
                    "Earache and fisticuffs? Take them elsewhere.")
                )
            except TypeError:
                rv.append(Trader.Patter(
                    self.here.proprietor,
                    random.choice([
                        "Hello, {0.name}".format(self.businesses[0].proprietor),
                        "What can I do for you?"
                    ])
                ))
            except Exception as e:
                print(e)

            finally:
                rv.extend(self.alerts)
                self.alerts = []

        return rv

    async def __call__(self, loop=None):
        """
        In a business location, the game is driven by user interaction.
        Clock ticks operate the game calendar.

        Outside of business locations, we wait for a clock tick and offer dialogue.

        """
        player = self.businesses[0].proprietor
        self.ensemble = [player] + addisonarches.scenario.common.ensemble

        while not Clock.public.running:
            await asyncio.sleep(0, loop=loop)

        while Clock.public.running:
            if self.here is None: # Not at a business
                seqList = OrderedDict(gather_installed("turberfield.interfaces.sequence", log=self._log))
                choice = next(iter(seqList.keys()), None)
                self._log.info("Selected sequence '{0}'.".format(choice))
                folder = seqList[choice]
                self.dialogueQueue = asyncio.Queue(maxsize=1, loop=loop)
                while folder:
                    folder = await run_through(
                        folder, self.ensemble, self.dialogueQueue, loop=loop)
                else:
                    self._log.info("Dialogue complete.")
                    self.dialogueQueue = None
                    self.shot = None
                    self.location = self.home

            await Clock.public.active.wait()
            self.declare(
                dict(
                    diorama=self.diorama,
                    frame=self.frame,
                    progress=self.progress,
                    inventory=self.inventory,
                    businesses=self.businesses
                ),
                loop=loop
            )
            await Clock.public.inactive.wait()

    @asyncio.coroutine
    def watch(self, q, **kwargs):
        loop = kwargs.pop("loop", None)
        msg = object()
        while msg is not None:
            msg = yield from q.get()
            self._log.debug(msg)
            for job in getattr(msg, "payload", []):
                try:
                    if isinstance(job, Ask):
                        self.drama.memory.append(job)
                    elif isinstance(job, Bid):
                        self.drama.memory.append(job)
                    elif isinstance(job, Buying):
                        ref = None
                        try:
                            ref = job.memory[0]
                            item = next(
                                i for i in
                                self.businesses[ref.owner].inventories[ref.location].contents
                                if i.label == ref.label and i.description == ref.description
                            )
                        except (AttributeError, IndexError, KeyError, StopIteration) as e:
                            self._log.warning(e)
                            self._log.debug(ref)
                        else:
                            self.drama = Buying(memory=[item])
                    elif isinstance(job, Game.Item):
                        # crafting
                        try:
                            item = next(
                                i for i in
                                self.businesses[job.owner].inventories[job.location].contents
                                if i.label == job.label and i.description == job.description
                            )
                            inv = self.here.inventories[self.location]
                            inv.contents[item] -= 1
                            inv.contents.update(item.components)
                        except:
                            # self.here != self.businesses[0]
                            self.alerts.append(Alert(
                                datetime.datetime.now(),
                                "You can't do that here.")
                            )
                            break

                    elif isinstance(job, Game.Via):
                        if self.destinations[job.id] == job.name:

                            yield from self.clock.advance(loop=loop)

                            self.location = job.name
                        else:
                            self._log.warning(job)

                    elif isinstance(job, Selling):
                        ref = job.memory[0]
                        try:
                            item = next(
                                i for i in
                                self.businesses[ref.owner].inventories[ref.location].contents
                                if i.label == ref.label and i.description == ref.description
                            )
                        except (KeyError, StopIteration) as e:
                            self._log.warning(ref)
                        else:
                            self.drama = Selling(memory=[item])
                    else:
                        if self.dialogueQueue is not None:
                            self._log.info("Waiting for dialogue...")
                            shot, item = yield from self.dialogueQueue.get()
                            if shot is not self.shot:
                                self.dialogue.clear()
                            if isinstance(item, Model.Line):
                                self.dialogue.append(item)
                            self.shot = shot
                            self.dialogueQueue.task_done()
                        else:
                            self.dialogue.clear()
                except Exception as e:
                    self._log.error(e)

            self.declare(
                dict(
                    diorama=self.diorama,
                    frame=self.frame,
                    progress=self.progress,
                    inventory=self.inventory
                )
            )

            if None not in (msg, self.down):
                msg = reply(msg.header)
                yield from self.down.put(msg)

def create_game(parent, user, name, token=None, down=None, up=None, loop=None):

    if None in (down, up):
        down = asyncio.Queue(loop=loop)
        up = asyncio.Queue(loop=loop)

    options = Clock.options(parent=parent)
    clock = Clock(loop=loop, **options)

    options = Game.options(Game.Player(user, name), parent=parent)
    game = Game(
        Game.Player(user, name),
        addisonarches.scenario.easy.businesses[:],
        clock,
        token,
        up,
        down=down,
        loop=loop,
        **options
    ).load()
    return (game, clock, down, up)

def init_game(game, clock, down, up, loop=None):
    loop.create_task(clock(loop=loop))
    loop.create_task(game(loop=loop))

    progress = Persistent.recent_slot(game._services["progress.rson"].path)
    return (progress, down, up)

def create(parent, user, name, token, down=None, up=None, loop=None):
    return init_game(
        *create_game(parent, user, name, token, down, up, loop=loop),
        loop=loop
    )

Assembly.register(
    Clock.Tick, Game.Avatar, Game.Drama, Game.Item, Game.Tally, Game.Via,
    Model.Line, Player
)
