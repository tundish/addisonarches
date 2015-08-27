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

import asyncio
import concurrent.futures
import logging
import numbers
import os.path
import sys
import tempfile
import unittest
import uuid

from addisonarches.business import Trader
from addisonarches.game import Clock
from addisonarches.game import Game
from addisonarches.game import Persistent
from addisonarches.scenario import Location
from addisonarches.scenario.types import Character
from addisonarches.utils import get_objects
from addisonarches.utils import group_by_type
from addisonarches.utils import query_object_chain
from addisonarches.utils import rson2objs
import addisonarches.scenario


class GameTests(unittest.TestCase):

    user = "someone@somewhere.net"

    @staticmethod
    def create_experts(parent, qIn, loop=None):
        options = Clock.options(parent=parent)
        clock = Clock(loop=loop, **options)

        options = Game.options(
            Game.Player(GameTests.user, "Player 1"),
            parent=parent
        )
        game = Game(
            Game.Player(GameTests.user, "Player 1"),
            addisonarches.scenario.businesses[:],
            clock,
            qIn, 
            loop=loop,
            **options
        )
        game.load()

        return (clock, game)

    @classmethod
    def setUpClass(cls):
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
        cls.asyncioDebug = os.environ.get("PYTHONASYNCIODEBUG", None)
        os.environ["PYTHONASYNCIODEBUG"] = str(True)

    @classmethod
    def tearDownClass(cls):
        logging.getLogger("asyncio").setLevel(logging.INFO)
        if "PYTHONASYNCIODEBUG" in os.environ:
            if cls.asyncioDebug is None:
                os.environ.pop("PYTHONASYNCIODEBUG")
            else:
                os.environ["PYTHONASYNCIODEBUG"] = cls.asyncioDebug

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        path = Persistent.Path(self.root.name, GameTests.user, None, None)
        Persistent.make_path(path)
        #print(path)

    def tearDown(self):
        self.loop.close()
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None
        Clock.public = None
        Game.public = None

    def run_test_async(self, coro):

        self.assertTrue(self.loop)

        def run_then_cancel(tasks, coro, game, q, loop):
            yield from asyncio.sleep(0, loop=loop)

            try:
                yield from coro(game, q, loop)
            finally:
                yield from q.put(None)
                yield from asyncio.sleep(0, loop=loop)
                for task in tasks:
                    task.cancel()

        q = asyncio.Queue(loop=self.loop)
        clock, game = GameTests.create_experts(
            self.root.name, q, loop=self.loop
        )
        tasks = [
            asyncio.Task(clock(loop=self.loop), loop=self.loop),
            asyncio.Task(game(loop=self.loop), loop=self.loop)
        ]

        tasks = asyncio.Task.all_tasks(self.loop)
        test = asyncio.Task(
            run_then_cancel(tasks, coro, game, q, loop=self.loop),
            loop=self.loop
        )
        done, pending = self.loop.run_until_complete(
            asyncio.wait(
                asyncio.Task.all_tasks(loop=self.loop),
                loop=self.loop,
                timeout=1
            )
        )
        e = test.exception()
        if e is not None:
            if isinstance(e, UserWarning):
                print(e, file=sys.stderr)
            else:
                raise e
        else:
            return (done, pending)

    def test_run_async_masks_no_failures(self):
        """
        Provoke failure and check it's detected from a wrapped coroutine.

        """
        @asyncio.coroutine
        def stimulus(game, q, loop=None):
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)
            self.assertEqual(0, len(objs[Location]))

        self.assertRaises(AssertionError, self.run_test_async, stimulus)

    def test_look(self):

        @asyncio.coroutine
        def stimulus(game, q, loop=None):
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)
            self.assertEqual(6, len(objs[Game.Via]))

            self.assertEqual(1, len(objs[Location]))
            self.assertTrue("Addison Arches 18a", query_object_chain(data, "capacity").name)

            self.assertEqual(1, len(objs[Clock.Tick]))
            self.assertTrue(query_object_chain(data, "ts").value.endswith("08:00:00"))

            self.assertEqual(1, len(objs[Game.Drama]))
            self.assertEqual(1, len(objs[Game.Tally]))
            self.assertIsInstance(objs[Game.Tally][0].value, numbers.Number)

            self.assertEqual(0, len(objs[Character]))
            self.assertEqual(0, len(objs[Trader.Patter]))

        done, pending = self.run_test_async(stimulus)

    def test_go(self):

        @asyncio.coroutine
        def stimulus(game, q, loop=None):
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)
            self.assertTrue(query_object_chain(data, "ts").value.endswith("08:00:00"))
            self.assertTrue("Addison Arches 18a", query_object_chain(data, "capacity").name)
            self.assertEqual(6, len(objs[Game.Via]))

            # Go to Kinh Ship Bulk Buy
            yield from q.put(objs[Game.Via][1])
            yield from asyncio.sleep(0, loop=loop)
            yield from asyncio.sleep(0, loop=loop)
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)

            self.assertEqual("Kinh Ship Bulk Buy", query_object_chain(data, "capacity").name)
            self.assertTrue(query_object_chain(data, "ts").value.endswith("08:30:00"))
            self.assertEqual(1, len(objs[Game.Via]))
            self.assertEqual(1, len(objs[Character]))
            self.assertEqual(1, len(objs[Game.Item]))
            self.assertEqual(1, len(objs[Trader.Patter]))

        done, pending = self.run_test_async(stimulus)

