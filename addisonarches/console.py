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
from decimal import Decimal
import itertools
import random
import sys
import uuid

import addisonarches.scenario
from addisonarches.scenario import CashBusiness
from addisonarches.scenario import Buying
from addisonarches.scenario import Character
from addisonarches.scenario import Location
from addisonarches.scenario import Selling
from addisonarches.valuation import Ask
from addisonarches.valuation import Bid


class Console(cmd.Cmd):

    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.prompt = "Type 'help' for commands > "

    @staticmethod
    def get_command(prompt):
        line = sys.stdin.readline()
        if not len(line):
            line = "EOF"
        else:
            line = line.rstrip("\r\n")
        return line

    @property
    def routines(self):
        return [self.command_loop, self.input_loop]

    @asyncio.coroutine
    def input_loop(self, commands, executor, loop=None):
        while not self.game.stop:
            try:
                line = yield from asyncio.wait_for(
                    loop.run_in_executor(
                        executor,
                        self.get_command,
                        self.prompt
                    ),
                    timeout=None,
                    loop=loop)
            except asyncio.TimeoutError:
                pass
                
            yield from commands.put(line)
 
    @asyncio.coroutine
    def command_loop(self, commands, executor, loop=None):
        self.preloop()
        while not self.game.stop:
            sys.stdout.write(self.prompt)
            sys.stdout.flush()
            line = yield from commands.get()
            try:
                line = self.precmd(line)
                stop = self.onecmd(line)
                self.game.stop = self.postcmd(stop, line)
            except Exception as e:
                print(e)
            try:
                self.game.ts = next(self.game.clock)
                self.prompt = "{:%A %H:%M} > ".format(
                    self.game.ts
                )
            except StopIteration:
                self.game.stop = True
            else:
                print("You're at {}.".format(self.game.location))
                mood = (self.game.drama.__class__.__name__.lower()
                        if self.game.drama is not None
                        else random.choice(
                            ["hopeful", "optimistic", "relaxed"]
                        ))
                print("You're in a {} mood.".format(mood))
                print("You've got £{0.tally:.2f} in the kitty.".format(
                    self.game.businesses[0]
                ))
                if self.game.here != self.game.businesses[0]:
                    print("{0.name} is nearby.".format(
                            self.game.here.proprietor
                    ))
                else:
                    print("Earache and fisticuffs? Take them elsewhere.")
        else:
            self.postloop()
            sys.stdout.write("Press return.")
            sys.stdout.flush()
            for task in asyncio.Task.all_tasks(loop):
                task.cancel()
            loop.stop()

    def precmd(self, line):
        return line

    def postcmd(self, stop, line):
        "Potential 'game over' decisions."
        self.game.here(game)
        try:
            self.preloop()
        except StopIteration:
            stop = True
        return stop

    def do_buy(self, arg):
        """
        'Buy' lists items you can buy. Supply a number from
        that menu to buy a specific item, eg::
            
            > buy
            (a list will be shown)

            > buy 3
        """
        line = arg.strip()
        view = self.game.here.inventories[self.game.location].contents.items()
        if not line:
            print("Here's what you can buy:")
            print(
                *["{0:01}: {1.label} ({2})".format(n, k, v)
                for n, (k, v) in enumerate(view)],
                sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            k, v = list(view)[int(line)]
            self.game.drama = Buying(iterable=[k])
        
    def do_bid(self, arg):
        """
        'Bid' offers money for an item, eg::

            > bid 35
        """
        line = arg.strip()
        if line.isdigit():
            bid = Bid(self.game.ts, int(line), "£")
            self.game.drama.memory.append(bid)
        
    def do_sell(self, arg):
        """
        'Sell' lists items you can sell. Supply a number from
        that menu to sell a specific item, eg::
            
            > sell
            (a list will be shown)

            > sell 3
        """
        line = arg.strip()
        view = (
            c for i in self.game.businesses[0].inventories.values()
            for c in i.contents.items())
        if not line:
            print("Here's what you can sell:")
            print(
                *["{0:01}: {1.label} ({2})".format(n, k, v)
                for n, (k, v) in enumerate(view)],
                sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            k, v = list(view)[int(line)]
            print(k, v)
        
    def do_go(self, arg):
        """
        'Go' lists places you can go. Supply a number from
        that menu to travel to a specific location, eg::
            
            > go
            (a list will be shown)

            > go 3
        """
        line = arg.strip()
        if not line:
            print("Here's where you can go:")
            print(*["{0:01}: {1}".format(n, i)
                    for n, i in enumerate(self.game.destinations)],
                    sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            self.game.location = self.game.destinations[int(line)]

    def do_look(self, arg):
        """
        'Look' tells you where you are and what you can see.
        Add a number from that menu to get specific details, eg::
            
            > look
            (a list will be shown)

            > look 2
            (more details may follow)
        """
        line = arg.strip()
        view = self.game.here.inventories[self.game.location].contents.items()
        if not line:
            print("Here's what you can see:")
            print(
                *["{0:01}: {1.label} ({2})".format(n, k, v)
                for n, (k, v) in enumerate(view) if v],
                sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            prefix = random.choice([
            "Dunno about the", "No details on the", "Just",
            ])
            k, v = list(view)[int(line)]
            print(k.description or "{prefix} {0}{1}.".format(
                k.label.lower(), ("s" if v > 1 else ""), prefix=prefix
            ))

    def do_split(self, arg):
        """
        'Split' tells you what you have that can be taken apart.
        Add a number from that menu to split that item up, eg::
            
            > split
            (a list will be shown)

            > split 2
            (more details may follow)
        """
        line = arg.strip()
        view = (
            (k, v)
            for k, v in self.game.here.inventories[
                self.game.location
            ].contents.items()
            if v and getattr(k, "components", None))
        if self.game.here != self.game.businesses[0]:
            print("You can't do that here.")
            return False
        if not line:
            print("Here's what you can split:")
            print(
                *["{0:01}: {1.label} ({2})".format(n, k, v)
                for n, (k, v) in enumerate(view)],
                sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            k, v = list(view)[int(line)]
            inv = self.game.here.inventories[self.game.location]
            inv.contents[k] -= 1
            inv.contents.update(k.components)

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

    def __init__(self, businesses):
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


if __name__ == "__main__":
    name = input("Please enter your name: ")
    proprietor = Character(uuid.uuid4().hex, name)
    locations = [Location("Addison Arches 18a", 100)]
    
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