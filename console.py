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
import cmd
from collections import namedtuple
import concurrent.futures
import datetime
import itertools

import scenario

@asyncio.coroutine
def game_loop(intervals, commands, executor, loop=None):
    yield from intervals.put(5)
    while True:
        line = yield from commands.get()
        yield from intervals.put(30)


@asyncio.coroutine
def user_input(intervals, commands, executor, loop=None, prompt="?"):
    yield from asyncio.sleep(0, loop=loop)
    while True:
        interval = yield from intervals.get()
        try:
            line = yield from asyncio.wait_for(
                    loop.run_in_executor(
                        executor,
                        input,
                        prompt
                    ),
                    interval,
                    loop=loop)
        except asyncio.TimeoutError:
            line = "wait"
        yield from commands.put(line)

 
class Game:

    def __init__(self, name, console):
        self.name = name
        self.console = console

class Console(cmd.Cmd):
    clock = (
        t for t in (
            datetime.datetime(year=2015, month=5, day=11) +
            datetime.timedelta(seconds=i)
            for i in itertools.islice(
                itertools.count(0, 30 * 60),
                7 * 24 * 60 // 30)
            )
        if 8 <= t.hour <= 19)
    prompt = "{:%A %H:%M} > ".format(next(clock))

    def postcmd(self, stop, line):
        try:
            self.prompt = "{:%A %H:%M} > ".format(next(self.clock))
        except StopIteration:
            stop = True
        return stop

    def do_go(self, arg):
        """
        Boo.
        """
        line = arg.strip()
        if not line:
            print(*["{0:01}: {1.name}".format(n, i)
                    for n, i in enumerate(scenario.locations)],
                  sep="\n")

    def do_quit(self, arg):
        """
        End the game.
        """
        return True

if __name__ == "__main__":
    name = input("Please enter your name: ")
    game = Game(name=name, console=Console())
    loop = asyncio.get_event_loop()
    intervals = asyncio.Queue()
    commands = asyncio.Queue()
    routines = [user_input, game_loop]
    executor = concurrent.futures.ThreadPoolExecutor(len(routines))
    tasks = [
        asyncio.Task(routine(intervals, commands, executor, loop=loop))
        for routine in routines
    ]
    try:
        loop.run_forever()
    finally:
        loop.close()
