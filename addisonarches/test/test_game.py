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
import os.path
import tempfile
import unittest
import uuid

from addisonarches.cli import rson2objs
from addisonarches.game import Clock
from addisonarches.game import Game
from addisonarches.game import Persistent
import addisonarches.scenario

class GameTests(unittest.TestCase):

    user = "someone@somewhere.net"

    @staticmethod
    def create_experts(parent, qIn, loop=None):
        options = Game.options(
            Game.Player(GameTests.user, "Player 1"),
            parent=parent
        )
        game = Game(
            Game.Player(GameTests.user, "Player 1"),
            addisonarches.scenario.businesses,
            qIn, 
            loop=loop,
            **options
        )
        game.load()

        options = Clock.options(parent=parent)
        clock = Clock(loop=loop, **options)
        return (clock, game)

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        path = Persistent.Path(self.root.name, GameTests.user, None, None)
        Persistent.make_path(path)

    def test_go(self):

        @asyncio.coroutine
        def stimulus(tasks, q, loop=None):
            game = next(i for i in tasks if isinstance(i, Game))
            service = game._services["progress.rson"]
            path = os.path.join(*Persistent.recent_slot(service.path))
            with open(path, 'r') as content:
                data = rson2objs(content.read(), (Game.Via,))
                print(data)

            # Collision id, actor, stage
            obj = (id(None), uuid.uuid4().hex, uuid.uuid4().hex)
            yield from q.put(obj)
            yield from q.put(None)
            for task in tasks.values():
                task.cancel()

        q = asyncio.Queue(loop=self.loop)
        tasks = {
            expert: asyncio.Task(expert(loop=self.loop), loop=self.loop)
            for expert in GameTests.create_experts(
                self.root.name, q, loop=self.loop
            )
        }
        tasks["stimulus"] = asyncio.Task(
            stimulus(tasks, q, loop=self.loop),
            loop=self.loop
        )

        self.loop.run_until_complete(
            asyncio.wait(
                asyncio.Task.all_tasks(loop=self.loop),
                loop=self.loop,
                timeout=1
            )
        )

    def tearDown(self):
        self.loop.close()
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None
        Clock.public = None
        Game.public = None
