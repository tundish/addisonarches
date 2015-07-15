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

import argparse
import ast
import asyncio
from collections import OrderedDict
from collections import namedtuple
import datetime
import itertools
import logging
import os
import os.path
import pickle
from pprint import pprint
import sys
import tempfile

from turberfield.utils.expert import Expert

DFLT_LOCN = os.path.expanduser(os.path.join("~", ".addisonarches"))

__doc__ = """
Encapsulates the game world in Addison Arches.
"""


class UnNamedPipe:

    def __init__(self, pipe:tuple, **kwargs):
        self.pipe = pipe
        self._in = os.fdopen(self.pipe[1], 'w', buffering=1, encoding="utf-8")
        self._out = os.fdopen(self.pipe[0], 'r', buffering=1, encoding="utf-8")

    def put_nowait(self, msg):
        """
        Put an item into the queue without blocking.
        """
        try:
            pprint(msg, stream=self._in, compact=True, width=sys.maxsize)
        except TypeError:  # 'compact' is new in Python 3.4
            pprint(msg, stream=self._in, width=sys.maxsize)
        finally:
            self._in.flush()

    def get(self):
        """
        Remove and return an item from the queue. If queue is empty,
        block until an item is available.
        """
        payload = self._out.readline().rstrip("\n")
        return ast.literal_eval(payload)

    def close(self):
        """
        Completes the use of the queue.
        """
        try:
            self._in.close()
            self._out.close()
        except:
            self.pipe = None
        finally:
            return self.pipe


class Persistent(Expert):

    Path = namedtuple("Path", ["root", "home", "slot", "file"])
    Pickled = namedtuple("Pickled", ["name", "path"])

    @staticmethod
    def make_path(path:Path, prefix="tmp", suffix=""):
        if path.slot is None:
            dctry = os.path.join(path.root, path.home)
            try:
                os.mkdir(dctry)
            except FileExistsError:
                pass
            if path.file is not None:
                slot = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dctry)
                return path._replace(slot=slot)
            else:
                return path
        else:
            return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def declare(self, data, loop=None):
        super().declare(self, data, loop)


class Game(Persistent):

    @staticmethod
    def options(
        user,
        parent=os.path.expanduser(os.path.join("~", ".addisonarches"))
    ):
        return OrderedDict([
            ("businesses.pkl", Persistent.Pickled(
                "businesses",
                Persistent.Path(parent, user, None, None)
            )),
        ])

    def __init__(self, businesses, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.businesses = businesses
        self.location = self.home
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
        self.drama = None
        self.ts = None

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

    @property
    def routines(self):
        return [self.clock_loop]

    @asyncio.coroutine
    def clock_loop(self, commands, executor, loop=None):
        while not self.stop:
            yield from asyncio.sleep(self.interval)
            yield from commands.put("wait")
            sys.stdout.write("\n")
            sys.stdout.flush()


def parser(descr=__doc__):
    rv = argparse.ArgumentParser(description=descr)
    rv.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    rv.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    rv.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    rv.add_argument(
        "--output", default=DFLT_LOCN,
        help="path to output directory [{}]".format(DFLT_LOCN))
    return rv


def run(game, args, pipe=None):
    addisonarches.scenario.businesses.insert(
        0, CashBusiness(proprietor, None, locations, tally=Decimal(1000)))
    game = Game(businesses=addisonarches.scenario.businesses)
    console = Console(game)
    loop = asyncio.get_event_loop()
    commands = asyncio.Queue(loop=loop)
    routines = console.routines + game.routines
    executor = concurrent.futures.ThreadPoolExecutor(len(routines))
    tasks = [
        asyncio.Task(routine(commands, executor, loop=loop))
        for routine in routines
    ]
    loop.run_forever()

def run():
    p = parser()
    args = p.parse_args()
    if args.version:
        sys.stdout.write(__version__ + "\n")
        rv = 0
    else:
        try:
            os.mkdir(args.output)
        except OSError:
            pass
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
