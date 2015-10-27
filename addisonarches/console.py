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
from collections import Counter
from collections import defaultdict
from collections import namedtuple
import concurrent.futures
import datetime
from decimal import Decimal
import getpass
import itertools
import operator
import os.path
import random
import sys
import uuid

from turberfield.ipc.message import Alert
from turberfield.ipc.message import parcel

from addisonarches.business import CashBusiness
from addisonarches.business import Buying
from addisonarches.business import Selling
from addisonarches.business import Trader

import addisonarches.game
from addisonarches.game import Clock
from addisonarches.game import Game
from addisonarches.game import Persistent

from addisonarches.scenario import Location
from addisonarches.scenario.types import Character

from addisonarches.utils import get_objects
from addisonarches.utils import group_by_type
from addisonarches.utils import query_object_chain

from addisonarches.valuation import Ask
from addisonarches.valuation import Bid


def create_local_console(progress, down, up, loop=None):
    console = Console(progress, down, up, loop=loop)
    executor = concurrent.futures.ThreadPoolExecutor(
        max(4, len(console.routines) + 1)
    )
    for coro in console.routines:
        loop.create_task(coro(executor, loop=loop))
    return console


class Console(cmd.Cmd):

    def __init__(self, progress, down, up, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress = progress
        self.down = down
        self.up = up
        self.commands = asyncio.Queue(loop=loop)
        self.prompt = "Type 'help' for commands > "
        self.ts = None

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
    def input_loop(self, executor, loop=None):
        line = ""
        while not line.lower().startswith("quit"):
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
                
            yield from self.commands.put(line)
 
    @asyncio.coroutine
    def command_loop(self, executor, loop=None):
        line = ""
        locn = None
        self.preloop()
        while not line.lower().startswith("quit"):
            sys.stdout.write(self.prompt)
            sys.stdout.flush()
            line = yield from self.commands.get()
            try:
                line = self.precmd(line)
                msg = self.onecmd(line)
                if msg is not None:
                    yield from self.up.put(msg)
                    reply = yield from self.down.get()
                stop = self.postcmd(msg, line)
                if stop:
                    # TODO: Send 'stop' msg to game (up)
                    break
            except Exception as e:
                print(e)

            data = get_objects(self.progress)
            objs = group_by_type(data)
            #print(*list(objs.items()), sep="\n")

            locn = next(iter(objs[Location]), None)
            print("You're at {}.".format(getattr(locn, "name", "?")))

            for bystander in objs[Character]:
                print("{0.name} is nearby.".format(bystander))

            drama = next(iter(objs[Game.Drama]), None)
            print("You're in a {0.mood} mood.".format(drama))

            tally = query_object_chain(data, "name", "cash")
            print("You've got {0.units}{0.value} in the kitty.".format(tally))

            for actor, patter in itertools.groupby(objs[Trader.Patter], operator.attrgetter("actor")):
                print("{0[1]} says, ".format(actor))
                phrases = list(patter)
                for n, phrase in enumerate(phrases):
                    if n == len(phrases) - 1:
                        print("'{0}'.".format(phrase.text.rstrip('.')))
                    else:
                        print("'{0.text}'".format(phrase))

            for alert in objs[Alert]:
                print("{0.text}".format(alert))

        self.postloop()
        sys.stdout.flush()
        for task in asyncio.Task.all_tasks(loop):
            task.cancel()
        loop.stop()

    def precmd(self, line):
        return line

    def postcmd(self, msg, line):
        "Potential 'game over' decisions."
        data = get_objects(self.progress)
        objs = group_by_type(data)
        tick = next(iter(objs[Clock.Tick]), None)
        self.ts = tick.ts
        t = datetime.datetime.strptime(tick.value, "%Y-%m-%d %H:%M:%S")
        self.prompt = "{:%A %H:%M} > ".format(t)
        # TODO: Send 'stop' to game (down)
        return line.startswith("quit") and msg is None

    def do_buy(self, arg):
        """
        'Buy' lists items you can buy. Supply a number from
        that menu to buy a specific item, eg::
            
            > buy
            (a list will be shown)

            > buy 3
        """
        line = arg.strip()
        #view = self.game.here.inventories[self.game.location].contents.items()
        data = get_objects(self.progress)
        progress = group_by_type(data)
        totals = Counter(progress[Game.Item])
        menu = list(set(progress[Game.Item]))

        if not line:
            print("Here's what you can buy:")
            print(
                *["{0:01}: {1.label} ({2})".format(n, i, totals[i])
                for n, i in enumerate(menu) if totals[i]],
                sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            item = menu[int(line)]
            drama = Buying(iterable=[item])
            msg = parcel(None, drama)
            return msg
        
    def do_ask(self, arg):
        """
        'Ask' demands money for an item, eg::

            > ask 50
        """
        line = arg.strip()
        if line.isdigit():
            offer = Ask(self.ts, int(line), "£")
            msg = parcel(None, offer)
            return msg
        
    def do_bid(self, arg):
        """
        'Bid' offers money for an item, eg::

            > bid 35
        """
        line = arg.strip()
        if line.isdigit():
            offer = Bid(self.ts, int(line), "£")
            msg = parcel(None, offer)
            return msg
        
    def do_sell(self, arg):
        """
        'Sell' lists items you can sell. Supply a number from
        that menu to sell a specific item, eg::
            
            > sell
            (a list will be shown)

            > sell 3
        """
        line = arg.strip()
        data = get_objects(self.progress._replace(file="inventory.rson"))
        view = Counter(data).items()
        if not line:
            print("Here's what you can sell:")
            print(
                *["{0:01}: {1.label} ({2})".format(n, k, v)
                for n, (k, v) in enumerate(view)],
                sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            k, v = list(view)[int(line)]
            drama = Selling(iterable=[k])
            msg = parcel(None, drama)
            return msg

    def do_go(self, arg):
        """
        'Go' lists places you can go. Supply a number from
        that menu to travel to a specific location, eg::
            
            > go
            (a list will be shown)

            > go 3
        """
        line = arg.strip()
        data = get_objects(self.progress)
        progress = group_by_type(data)

        if not line:
            print("Here's where you can go:")
            print(*["{0:01}: {1}".format(i.id, i.name) for i in progress[Game.Via]],
                    sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            via = progress[Game.Via][int(line)]
            msg = parcel(None, via)
            return msg

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
        data = get_objects(self.progress)
        progress = group_by_type(data)
        totals = Counter(progress[Game.Item])
        menu = list(set(progress[Game.Item]))

        if not line:
            print("Here's what you can see:")
            if menu:
                print(
                    *["{0:01}: {1.label} ({2})".format(n, i, totals[i])
                    for n, i in enumerate(menu) if totals[i]],
                    sep="\n")
        elif line.isdigit():
            prefix = random.choice([
            "Dunno about the", "No details on the", "Just",
            ])
            item = menu[int(line)]
            print(item.description or "{prefix} {0}{1}.".format(
                item.label.lower(), ("s" if totals[item] > 1 else ""), prefix=prefix
            ))
        sys.stdout.write("\n")

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
        data = [i
            for i in get_objects(self.progress._replace(file="inventory.rson"))
            if i.type == "Compound"
        ]
        view = Counter(data).items()
        if not line:
            print("Here's what you can split:")
            print(
                *["{0:01}: {1.label} ({2})".format(n, k, v)
                for n, (k, v) in enumerate(view)],
                sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            k, v = list(view)[int(line)]
            msg = parcel(None, k)
            return msg

    def do_wait(self, arg):
        """
        Pass the time quietly.
        """
        return None

    def do_quit(self, arg):
        """
        End the game.
        """
        return None


def main(args):
    user = getpass.getuser()
    name = input("Please enter your name: ")
    path = Persistent.Path(args.output, user, None, None)
    Persistent.make_path(path)

    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    #down = asyncio.Queue(loop=loop)
    #up = asyncio.Queue(loop=loop)

    #tok = token(args.connect, APP_NAME)
    #node = create_udp_node(loop, tok, down, up)
    #loop.create_task(node(token=tok))
    progress, down, up = addisonarches.game.create(
        args.output, user, name, loop=loop
    )
    console = create_local_console(progress, down, up, loop=loop)

    try:
        loop.run_forever()
    except concurrent.futures.CancelledError:
        pass
    finally:
        loop.close()

    return 0
