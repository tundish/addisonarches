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
import datetime
import logging
import numbers
import os.path
import pathlib
import sys
import tempfile
import unittest
import uuid
import warnings

from turberfield.ipc.fsdb import token
from turberfield.ipc.message import Address
from turberfield.ipc.message import Alert
from turberfield.ipc.message import parcel
from turberfield.ipc.node import create_udp_node

from addisonarches.business import Buying
from addisonarches.business import Trader

from addisonarches.game import Clock
from addisonarches.game import Game
from addisonarches.game import Persistent
from addisonarches.game import create_game
from addisonarches.game import init_game

import addisonarches.scenario
from addisonarches.scenario import Location
from addisonarches.scenario.types import Character

from addisonarches.utils import get_objects
from addisonarches.utils import group_by_type
from addisonarches.utils import query_object_chain
from addisonarches.utils import registry
from addisonarches.utils import rson2objs


class TestUsesNode(unittest.TestCase):

    user = "someone@somewhere.net"
    connect = pathlib.PurePath(
        os.path.abspath(
            os.path.expanduser(
                os.path.join("~", ".turberfield")
            )
        )
    ).as_uri()

    @classmethod
    def setUpClass(cls):
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
        cls.asyncioDebug = os.environ.get("PYTHONASYNCIODEBUG", None)
        os.environ["PYTHONASYNCIODEBUG"] = str(True)
        cls.token = token(TestUsesNode.connect, "addisonarches.test.test_game")

    @classmethod
    def tearDownClass(cls):
        logging.getLogger("asyncio").setLevel(logging.INFO)
        if "PYTHONASYNCIODEBUG" in os.environ:
            if cls.asyncioDebug is None:
                os.environ.pop("PYTHONASYNCIODEBUG")
            else:
                os.environ["PYTHONASYNCIODEBUG"] = cls.asyncioDebug
        cls.token = None

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(None)

        #path = Persistent.Path(self.root.name, GameTests.user, None, None)
        #self.path = Persistent.make_path(path)

    def tearDown(self):
        self.loop.close()
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None
        Clock.public = None
        Game.public = None

    def run_test_async(self, coro, loop=None):

        self.assertTrue(loop)

        def run_then_cancel(coro, progress, down, up, loop):
            yield from asyncio.sleep(0, loop=loop)

            try:
                rv = yield from coro(progress, down, up, loop=loop)
            finally:
                msg = parcel(
                        self.token,
                        Alert(datetime.datetime.now(), "Hello World!"),
                        dst=Address(
                            self.token.namespace,
                            self.token.user,
                            self.token.service,
                            "addisonarches.test.game"
                        )
                    )
                yield from down.put(msg)
                yield from asyncio.sleep(0, loop=loop)
                for task in asyncio.Task.all_tasks(loop=loop):
                    task.cancel()


        def game_setup(loop, output):
            down = asyncio.Queue(loop=loop)
            up = asyncio.Queue(loop=loop)

            tok = token(TestUsesNode.connect, "addisonarches.test.game")
            node = create_udp_node(loop, tok, down, up, types=registry)
            loop.create_task(node(token=tok))

            game, clock, down, up = create_game(
                output, user=TestUsesNode.user, name="test",
                down=down, up=up, loop=loop
            )
            progress, down, up = init_game(
                game, clock, down, up, loop=self.loop
            )

            return progress

        progress = game_setup(loop, self.root.name)
        down = asyncio.Queue(loop=loop)
        up = asyncio.Queue(loop=loop)

        node = create_udp_node(loop, self.token, down, up, types=registry)
        loop.create_task(node(token=self.token))

        test = loop.create_task(
            run_then_cancel(coro, progress, down, up, loop=loop)
        )
        try:
            rv = loop.run_until_complete(asyncio.wait_for(test, 3, loop=loop))
        except concurrent.futures.CancelledError:
            rv = None
        finally:
            loop.close()

        e = test.exception()
        if e is not None:
            if isinstance(e, UserWarning):
                print(e, file=sys.stderr)
            else:
                raise e
        else:
            return rv

    def test_run_async_masks_no_failures(self):
        """
        Provoke failure and check it's detected from a wrapped coroutine.

        """
        @asyncio.coroutine
        def stimulus(progress, down, up, loop=None):
            data = get_objects(progress, types=registry)
            objs = group_by_type(data)
            self.assertEqual(0, len(objs[Location]))
            return objs

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            #self.run_test_async(stimulus, loop=self.loop)
            self.assertRaises(
                AssertionError,
                self.run_test_async, stimulus, loop=self.loop
            )

class GameTests(unittest.TestCase):

    user = "someone@somewhere.net"
    connect = pathlib.PurePath(
        os.path.abspath(
            os.path.expanduser(
                os.path.join("~", ".turberfield")
            )
        )
    ).as_uri()

    @classmethod
    def setUpClass(cls):
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
        cls.asyncioDebug = os.environ.get("PYTHONASYNCIODEBUG", None)
        os.environ["PYTHONASYNCIODEBUG"] = str(True)
        cls.token = token(GameTests.connect, "addisonarches.test.test_game")

    @classmethod
    def tearDownClass(cls):
        logging.getLogger("asyncio").setLevel(logging.INFO)
        if "PYTHONASYNCIODEBUG" in os.environ:
            if cls.asyncioDebug is None:
                os.environ.pop("PYTHONASYNCIODEBUG")
            else:
                os.environ["PYTHONASYNCIODEBUG"] = cls.asyncioDebug
        cls.token = None

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(None)

        #path = Persistent.Path(self.root.name, GameTests.user, None, None)
        #self.path = Persistent.make_path(path)

    def tearDown(self):
        self.loop.close()
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None
        Clock.public = None
        Game.public = None

    def run_test_async(self, coro, loop=None):

        self.assertTrue(loop)

        def run_then_cancel(coro, progress, down, up, loop):
            yield from asyncio.sleep(0, loop=loop)

            try:
                yield from coro(progress, down, up, loop=loop)
            finally:
                msg = parcel(
                        self.token,
                        Alert(datetime.datetime.now(), "Hello World!"),
                        dst=Address(
                            self.token.namespace,
                            self.token.user,
                            self.token.service,
                            "addisonarches.test.game"
                        )
                    )
                yield from down.put(msg)
                yield from asyncio.sleep(0, loop=loop)
                for task in asyncio.Task.all_tasks(loop=loop):
                    task.cancel()

        def game_setup(loop, output):
            down = asyncio.Queue(loop=loop)
            up = asyncio.Queue(loop=loop)

            tok = token(GameTests.connect, "addisonarches.test.game")
            node = create_udp_node(loop, tok, down, up, types=registry)
            loop.create_task(node(token=tok))

            game, clock, down, up = create_game(
                output, user=GameTests.user, name="test",
                down=down, up=up, loop=loop
            )
            progress, down, up = init_game(
                game, clock, down, up, loop=self.loop
            )

            return progress

        progress = game_setup(loop, self.root.name)
        down = asyncio.Queue(loop=loop)
        up = asyncio.Queue(loop=loop)

        node = create_udp_node(loop, self.token, down, up, types=registry)
        loop.create_task(node(token=self.token))

        test = loop.create_task(
            run_then_cancel(coro, progress, down, up, loop=loop)
        )
        try:
            rv = loop.run_until_complete(asyncio.wait_for(test, 3, loop=loop))
        except concurrent.futures.CancelledError:
            rv = None
        finally:
            loop.close()

        e = test.exception()
        if e is not None:
            if isinstance(e, UserWarning):
                print(e, file=sys.stderr)
            else:
                raise e
        else:
            return rv

    def test_run_async_masks_no_failures(self):
        """
        Provoke failure and check it's detected from a wrapped coroutine.

        """
        @asyncio.coroutine
        def stimulus(progress, down, up, loop=None):
            data = get_objects(progress, types=registry)
            objs = group_by_type(data)
            self.assertEqual(0, len(objs[Location]))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertRaises(
                AssertionError,
                self.run_test_async, stimulus, loop=self.loop
            )

    def test_look(self):

        @asyncio.coroutine
        def stimulus(progress, down, up, loop=None):
            data = get_objects(progress)
            objs = group_by_type(data)
            self.assertEqual(6, len(objs[Game.Via]))

            self.assertEqual(1, len(objs[Location]))
            self.assertTrue("Addison Arches 18a", query_object_chain(data, "capacity").name)

            self.assertEqual(1, len(objs[Clock.Tick]))
            self.assertTrue(objs[Clock.Tick][0].value.endswith("08:00:00"))

            self.assertEqual(1, len(objs[Game.Drama]))
            self.assertEqual(1, len(objs[Game.Tally]))
            self.assertIsInstance(objs[Game.Tally][0].value, numbers.Number)

            self.assertEqual(0, len(objs[Character]))
            self.assertEqual(0, len(objs[Trader.Patter]))

            self.assertEqual(1, len(objs[Alert]))

        rv = self.run_test_async(stimulus, loop=self.loop)

    def test_go(self):

        @asyncio.coroutine
        def stimulus(progress, down, up, loop=None):
            data = get_objects(progress)
            objs = group_by_type(data)
            self.assertTrue(objs[Clock.Tick][0].value.endswith("08:00:00"))
            self.assertTrue("Addison Arches 18a", query_object_chain(data, "capacity").name)
            self.assertEqual(6, len(objs[Game.Via]))

            # Go to Kinh Ship Bulk Buy
            msg = parcel(
                self.token,
                objs[Game.Via][1],
                dst=Address(
                    self.token.namespace,
                    self.token.user,
                    self.token.service,
                    "addisonarches.test.game"
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()
            self.assertEqual(msg.header.id, reply.header.id)
            
            data = get_objects(progress)
            objs = group_by_type(data)

            self.assertEqual("Kinh Ship Bulk Buy", query_object_chain(data, "capacity").name)
            self.assertTrue(objs[Clock.Tick][0].value.endswith("08:30:00"))
            self.assertEqual(1, len(objs[Game.Via]))
            self.assertEqual(1, len(objs[Character]))
            self.assertEqual(3, len(objs[Game.Item]))
            self.assertEqual(1, len(objs[Trader.Patter]))

        rv = self.run_test_async(stimulus, loop=self.loop)

    def test_buy(self):

        @asyncio.coroutine
        def stimulus(progress, down, up, loop=None):
            data = get_objects(progress)
            objs = group_by_type(data)
            self.assertTrue(objs[Clock.Tick][0].value.endswith("08:00:00"))
            self.assertTrue("Addison Arches 18a", query_object_chain(data, "capacity").name)
            self.assertEqual(6, len(objs[Game.Via]))

            # Go to Kinh Ship Bulk Buy
            msg = parcel(
                self.token,
                objs[Game.Via][1],
                dst=Address(
                    self.token.namespace,
                    self.token.user,
                    self.token.service,
                    "addisonarches.test.game"
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()

            data = get_objects(progress)
            objs = group_by_type(data)
            drama = objs[Game.Drama][0]
            self.assertEqual(type(None).__name__, drama.type)

            self.assertEqual("Kinh Ship Bulk Buy", query_object_chain(data, "capacity").name)

            # TODO: Send Buying drama
            item = objs[Game.Item][0]
            msg = parcel(
                self.token,
                Buying(iterable=[item]),
                dst=Address(
                    self.token.namespace,
                    self.token.user,
                    self.token.service,
                    "addisonarches.test.game"
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()

            data = get_objects(progress)
            objs = group_by_type(data)

            drama = objs[Game.Drama][0]
            self.assertEqual("buying", drama.mood)

            nearby = objs[Character][0]
            self.assertEqual("Jimmy Wei Zhang", nearby.name)

        rv = self.run_test_async(stimulus, loop=self.loop)
