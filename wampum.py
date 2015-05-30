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
import sys

import scenario

__doc__ + """
Commodity items in their millions (eg: shells): named tuples
Combine commodities to make objects (eg: shells + string -> wampum): classes
Modify objects by mixing (eg: wampum + shape -> belt)
Innovate objects by subclassing (eg: belt + speech -> influence) Influence is a commodity!
Break down objects to commodities again.

"""

class Console(cmd.Cmd):

    @staticmethod
    def get_command(prompt):
        line = sys.stdin.readline()
        if not len(line):
            line = "EOF"
        else:
            line = line.rstrip("\r\n")
        return line

    def precmd(self, line):
        return line

    def postcmd(self, stop, line):
        try:
            self.preloop()
        except StopIteration:
            stop = True
        return stop

    def do_go(self, arg):
        """
        Travel to another location.
        """
        line = arg.strip()
        if not line:
            print(*["{0:01}: {1.name}".format(n, i)
                    for n, i in enumerate(scenario.locations)],
                  sep="\n")

    def do_wait(self, arg):
        """
        Pass the time quietly.
        """
        return False

    def do_quit(self, arg):
        """
        End the game.
        """
        return True

class Game:

    def __init__(self, name, console):
        self.name = name
        self.console = console
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
        self.prompt = "Type 'help' for commands > "

    def setup(self, loop=None):
        commands = asyncio.Queue()
        routines = [self.console_loop, self.input_loop, self.clock_loop]
        executor = concurrent.futures.ThreadPoolExecutor(len(routines))
        return [
            asyncio.Task(routine(commands, executor, loop=loop))
            for routine in routines
        ]

    @asyncio.coroutine
    def clock_loop(self, commands, executor, loop=None):
        while not self.stop:
            yield from asyncio.sleep(self.interval)
            yield from commands.put("wait")
            sys.stdout.write("\n")
            sys.stdout.flush()

    @asyncio.coroutine
    def console_loop(self, commands, executor, loop=None):
        console = self.console()
        console.preloop()
        while not self.stop:
            sys.stdout.write(self.prompt)
            sys.stdout.flush()
            line = yield from commands.get()
            line = console.precmd(line)
            stop = console.onecmd(line)
            self.stop = console.postcmd(stop, line)
            try:
                self.prompt = "{:%A %H:%M} > ".format(
                    next(self.clock)
                )
            except StopIteration:
                self.stop = True
        else:
            console.postloop()
            sys.stdout.write("Press return.")
            sys.stdout.flush()
            for task in asyncio.Task.all_tasks(loop):
                task.cancel()
            loop.stop()

    @asyncio.coroutine
    def input_loop(self, commands, executor, loop=None):
        while not self.stop:
            try:
                line = yield from asyncio.wait_for(
                    loop.run_in_executor(
                        executor,
                        self.console.get_command,
                        self.prompt
                    ),
                    timeout=None,
                    loop=loop)
            except asyncio.TimeoutError:
                pass
                
            yield from commands.put(line)
 
if __name__ == "__main__":
    name = input("Please enter your name: ")
    game = Game(name=name, console=Console)
    loop = asyncio.get_event_loop()
    game.setup(loop)
    loop.run_forever()
