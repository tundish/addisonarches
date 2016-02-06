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
import logging
from logging.handlers import WatchedFileHandler
import os
import sys

from turberfield.ipc.fsdb import token
from turberfield.ipc.node import create_udp_node

from addisonarches.cli import parsers
import addisonarches.console
import addisonarches.web.main


__doc__ = """
Main entry point for Addison Arches game.

TODO: Launch game only.

Move invocation of console, web elsewhere.
"""

def main(args):
    log = logging.getLogger("addisonarches.main")
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    down = asyncio.Queue(loop=loop)
    up = asyncio.Queue(loop=loop)

    #TODO: Read service name from CLI
    service = "dev"  # Cf qa, demo, prod, etc
    tok = token(args.connect, service, args.session)
    node = create_udp_node(loop, tok, down, up)
    loop.create_task(node(token=tok))

    progress, down, up = addisonarches.game.create(
        args.output, args.session, args.name,
        tok, down=down, up=up, loop=loop
    )
    loop.run_forever()

def run():
    p, subs = parsers()
    p.add_argument(
        "--session", required=True,
        help="Unique id of session.")
    p.add_argument(
        "--name", required=True,
        help="Player name.")
    args = p.parse_args()

    rv = 0
    if args.version:
        sys.stdout.write(addisonarches.__version__ + "\n")
    else:
        rv = main(args)

    sys.exit(rv)

if __name__ == "__main__":
    run()
