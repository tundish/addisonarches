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

from turberfield.utils.expert import TypesEncoder

from addisonarches import __version__
from addisonarches.cli import add_common_options
from addisonarches.cli import add_web_options
import addisonarches.game
from addisonarches.utils import send
from addisonarches.web.services import Assets
from addisonarches.web.services import Registration
from addisonarches.web.services import Transitions
from addisonarches.web.services import Workflow

__doc__ = """
Runs the web interface for Addison Arches.
"""

#@app.route("/", "GET")
def home_get():
    # TODO: Get game name
    log = logging.getLogger("addisonarches.web.home")
    userId = authenticated_userid(bottle.request)
    log.info(userId)
    args = app.config.get("args")
    send(args)
    path = os.path.join(
        app.config["args"].output, "player.rson"
    )
    ts = time.time()
    actor = None
    page = {
        "info": {
            "actor": actor,
            "interval": 200,
            "refresh": None,
            "time": "{:.1f}".format(ts),
            "title": "Addison Arches {}".format(__version__),
            "version": __version__
        },
        "nav": [],
        "items": [],
        "options": [],
    }
    try:
        pass
    except Exception as e:
        log.exception(e)
    finally:
        return json.dumps(
            page, cls=TypesEncoder, indent=4
        )

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

    # TODO: Make a Turberfield-ipc node
    #tok = token(args.connect, APP_NAME)
    #node = create_udp_node(loop, tok, down, up)

    app = aiohttp.web.Application()
    assets = Assets(app, **vars(args))
    reg = Registration(app, **vars(args))
    transitions = Transitions(app, **vars(args))
    work = Workflow(app, **vars(args))

    loop = asyncio.get_event_loop()
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
