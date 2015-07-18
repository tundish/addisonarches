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
import getpass
import itertools
import random
import sys
import uuid

from addisonarches.business import Buying
from addisonarches.business import CashBusiness
from addisonarches.business import Selling
from addisonarches.game import Game
from addisonarches.game import Persistent
import addisonarches.scenario
from addisonarches.scenario import Location
from addisonarches.scenario.types import Character
from addisonarches.valuation import Ask
from addisonarches.valuation import Bid


# TODO: Coroutine to check game status, update prompt of necessary,
# then
#           sys.stdout.write("\n")
#           sys.stdout.flush()


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
        try:
            handler = self.game.here.handler(self.game.drama)
            reaction = handler(self.game.drama, self.game)
        except AttributeError:
            # Player business is not a Handler subclass
            pass
        except TypeError as e:
            greeting = random.choice(
                ["Hello, {0.name}".format(
                    self.game.businesses[0].proprietor
                ), "What can I do for you?"]
            )
            print("{0.name} says, '{1}'.".format(
                    self.game.here.proprietor, greeting
                 )
            )
        else:
            for msg in reaction:
                print(msg)
        try:
            self.prompt = "{:%A %H:%M} > ".format(
                self.game.ts
            )
        except StopIteration:
            stop = True

        self.game.stop = stop
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
        
    def do_ask(self, arg):
        """
        'Ask' demands money for an item, eg::

            > ask 50
        """
        line = arg.strip()
        if line.isdigit():
            offer = Ask(self.game.ts, int(line), "£")
            self.game.drama.memory.append(offer)
        
    def do_bid(self, arg):
        """
        'Bid' offers money for an item, eg::

            > bid 35
        """
        line = arg.strip()
        if line.isdigit():
            offer = Bid(self.game.ts, int(line), "£")
            self.game.drama.memory.append(offer)
        
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
            self.game.drama = Selling(iterable=[k])
        
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
        self.game.ts = next(self.game.clock)

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


def main(args):
    user = getpass.getuser()
    name = input("Please enter your name: ")
    path = Persistent.Path(args.output, user, None, None)
    Persistent.make_path(path)

    options = Game.options(Game.Player(user, name), parent=args.output)
    game = Game(
        Game.Player(user, name),
        addisonarches.scenario.businesses,
        **options
    )
    game.load()
    console = Console(game)
    loop = asyncio.get_event_loop()
    commands = asyncio.Queue(loop=loop)
    executor = concurrent.futures.ThreadPoolExecutor(
        max(4, len(console.routines) + 1)
    )
    tasks = [
        asyncio.Task(routine(commands, executor, loop=loop))
        for routine in console.routines
    ]
    tasks.append(asyncio.Task(game(commands, executor, loop=loop)))
    try:
        loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))
    except concurrent.futures.CancelledError:
        pass

    return 0
