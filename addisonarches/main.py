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
import os
import sys


from addisonarches.cli import add_console_command_parser
from addisonarches.cli import add_web_command_parser
from addisonarches.cli import parsers
import addisonarches.console
import addisonarches.web.main
from addisonarches.worker import subprocess_queue_factory


__doc__ = """
Main entry point for Addison Arches game.

TODO: Launch game only.

Move invocation of console, web elsewhere.
"""

def main(args):
    rv = 0
    if args.command == "console":
        rv = addisonarches.console.main(args)
    elif args.command == "web":
        if os.name == "nt":
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        # TODO: Spawn N==1 web processes
        # TODO: Create node and invoke Game object in this process
        queue = asyncio.Queue(loop=loop)
        transport = loop.run_until_complete(
            loop.subprocess_exec(
                subprocess_queue_factory(queue, loop),
                sys.executable,
                "-m", "addisonarches.web.main",
                *["--{}={}".format(i, getattr(args, i))
                for i in  ("output", "host", "port")] 
            )
        )[0]
        loop.run_forever()
    return rv


def run():
    p, subs = parsers()
    add_console_command_parser(subs)
    add_web_command_parser(subs)
    args = p.parse_args()

    rv = 0
    if args.version:
        sys.stdout.write(addisonarches.__version__ + "\n")
    else:
        rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Missing command.\n\n")
        p.print_help()

    sys.exit(rv)

if __name__ == "__main__":
    run()
