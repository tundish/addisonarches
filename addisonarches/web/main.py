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


import argparse
import asyncio
import functools
import logging
import os
import sys

import aiohttp.web

from turberfield.ipc.cli import add_common_options
from turberfield.ipc.node import create_udp_node

from addisonarches import __version__
from addisonarches.cli import add_game_options
from addisonarches.cli import add_web_options
import addisonarches.game
from turberfield.ipc.fsdb import token
from addisonarches.web.services import APP_NAME
from addisonarches.web.services import Assets
from addisonarches.web.services import Registration
from addisonarches.web.services import Transitions
from addisonarches.web.services import Workflow

__doc__ = """
Runs the web interface for Addison Arches.
"""

def main(args):
    log = logging.getLogger("addisonarches.web")
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

    #TODO: turberfield-ipc must accept service name
    tok = token(args.connect, APP_NAME)
    node = create_udp_node(loop, tok, down, up)
    loop.create_task(node(token=tok))

    app = aiohttp.web.Application()
    assets = Assets(app, **vars(args))
    reg = Registration(app, tok, down, up, **vars(args))
    transitions = Transitions(app, **vars(args))
    work = Workflow(app, tok, down, up, **vars(args))
    for svc in (assets, reg, transitions, work):
        log.info("{0.__class__.__name__} object serves {1}".format(
            svc, ", ".join(svc.routes.keys())))

    handler = app.make_handler()
    f = loop.create_server(handler, args.host, args.port)
    srv = loop.run_until_complete(f)

    log.info("Serving on {0[0]}:{0[1]}".format(srv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(handler.finish_connections(1.0))
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.finish())
    loop.close()

def run():
    p = argparse.ArgumentParser(
        __doc__,
        fromfile_prefix_chars="@"
    )
    p = add_common_options(p)
    p = add_game_options(p)
    p = add_web_options(p)
    args = p.parse_args()
    if args.version:
        sys.stderr.write(__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
