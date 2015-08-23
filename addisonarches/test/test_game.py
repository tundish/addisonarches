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
import functools
import logging
import os.path
import tempfile
import unittest
import uuid

from addisonarches.cli import rson2objs
from addisonarches.cli import group_by_type
from addisonarches.cli import query_object_chain
from addisonarches.game import Clock
from addisonarches.game import Game
from addisonarches.game import Persistent
import addisonarches.scenario
from addisonarches.scenario import Location
from addisonarches.scenario.types import Character


def get_objects(expert, name="progress.rson"):
    service = expert._services[name]
    path = os.path.join(*Persistent.recent_slot(service.path))
    with open(path, 'r') as content:
        data = rson2objs(
            content.read(),
            (Clock.Tick, Location, Game.Via,)
        )
    return data


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
            addisonarches.scenario.businesses,
            clock,
            qIn, 
            loop=loop,
            **options
        )
        game.load()

        return (clock, game)

    @classmethod
    def setUpClass(cls):
        cls.asyncioDebug = os.environ.get("PYTHONASYNCIODEBUG", None)
        #os.environ["PYTHONASYNCIODEBUG"] = str(True)

    @classmethod
    def tearDownClass(cls):
        if "PYTHONASYNCIODEBUG" in os.environ:
            if cls.asyncioDebug is None:
                os.environ.pop("PYTHONASYNCIODEBUG")
            else:
                os.environ["PYTHONASYNCIODEBUG"] = cls.asyncioDebug

    def setUp(self):
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
        self.root = tempfile.TemporaryDirectory()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        path = Persistent.Path(self.root.name, GameTests.user, None, None)
        Persistent.make_path(path)

    def run_test_async(self, coro):

        def run_then_cancel(coro, loop=None):
            """
            Wraps the test coroutine in code which cleans up other game
            tasks afterwards.

            Returns a coroutine.
            """

            tasks = asyncio.Task.all_tasks(loop)

            @functools.wraps(coro)
            @asyncio.coroutine
            def inner(game, q, loop=loop):
                try:
                    yield from coro(game, q, loop)
                finally:
                    yield from q.put(None)
                    yield from asyncio.sleep(0, loop=loop)
                    for task in tasks:
                        task.cancel()
            return inner

        q = asyncio.Queue(loop=self.loop)
        clock, game = GameTests.create_experts(
            self.root.name, q, loop=self.loop
        )
        tasks = [
            asyncio.Task(clock(loop=self.loop), loop=self.loop),
            asyncio.Task(game(loop=self.loop), loop=self.loop)
        ]

        test = asyncio.Task(
            run_then_cancel(coro, loop=self.loop)(game, q, loop=self.loop),
            loop=self.loop
        )
        done, pending = self.loop.run_until_complete(
            asyncio.wait(
                asyncio.Task.all_tasks(loop=self.loop),
                loop=self.loop,
                timeout=1
            )
        )
        return (done, pending)

    @unittest.expectedFailure
    def test_run_async_masks_no_failures(self):
        """
        Provoke failure and check it's detected from a wrapped coroutine.

        """
        @asyncio.coroutine
        def stimulus(game, tasks, q, loop=None):
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)
            self.assertEqual(0, len(objs[Location]))

        done, pending = self.run_test_async(stimulus)

    def tost_look(self):

        @asyncio.coroutine
        def stimulus(game, tasks, q, loop=None):
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)
            self.assertEqual(1, len(objs[Location]))
            self.assertTrue(query_object_chain(data, "ts").value.endswith("08:00:00"))
            self.assertTrue("Addison Arches 18a", query_object_chain(data, "capacity").name)
            self.assertEqual(1, len(objs[Clock.Tick]))
            self.assertEqual(6, len(objs[Game.Via]))
            self.assertEqual(0, len(objs[Location]))

        done, pending = self.run_test_async(stimulus)
        print(done)
        print(pending)

    def tost_go(self):

        @asyncio.coroutine
        def stimulus(game, tasks, q, loop=None):
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)
            self.assertTrue(query_object_chain(data, "ts").value.endswith("08:00:00"))
            self.assertTrue("Addison Arches 18a", query_object_chain(data, "capacity").name)
            self.assertEqual(6, len(objs[Game.Via]))

            # Go to Kinh Ship Bulk Buy
            yield from q.put(objs[Game.Via][1])
            for _ in range(len(tasks)):
                yield from asyncio.sleep(0, loop=loop)
            data = get_objects(game, "progress.rson")
            objs = group_by_type(data)

            self.assertEqual("Kinh Ship Bulk Buy", query_object_chain(data, "capacity").name)
            self.assertTrue(query_object_chain(data, "ts").value.endswith("08:30:00"))
            self.assertEqual(1, len(objs[Game.Via]))
            yield from q.put(None)
            for task in tasks:
                task.cancel()

        self.run_async(stimulus)

    def tearDown(self):
        self.loop.close()
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None
        Clock.public = None
        Game.public = None
