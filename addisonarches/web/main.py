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
from collections import OrderedDict
import concurrent.futures
import logging
import os
import sys
import time

import bottle
from bottle import Bottle
import pkg_resources

from addisonarches import __version__
import addisonarches.game

__doc__ = """
Runs the web interface for Addison Arches.
"""

bottle.TEMPLATE_PATH.append(
    pkg_resources.resource_filename("addisonarches.web", "templates")
)

app = Bottle()

@app.route("/titles", "GET")
@bottle.view("titles")
def titles_get():
    log = logging.getLogger("addisonarches.web.titles")

    items = []
    return {
        "info": {
            "args": app.config.get("args"),
            "debug": bottle.debug,
            "interval": 200,
            "time": "{:.1f}".format(time.time()),
            "title": "Addison Arches {}".format(__version__),
            "version": __version__
        },
        "items": OrderedDict([(str(id(i)), i) for i in items]),
        
    }

@app.route("/audio/<filepath:path>")
def serve_audio(filepath):
    log = logging.getLogger("addisonarches.web.serve_audio")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/audio"
    )
    return bottle.static_file(filepath, root=locn)


@app.route("/css/<filepath:path>")
def serve_css(filepath):
    log = logging.getLogger("addisonarches.web.serve_css")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/css"
    )
    return bottle.static_file(filepath, root=locn)


@app.route("/img/<filepath:path>")
def serve_img(filepath):
    log = logging.getLogger("addisonarches.web.serve_img")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/img"
    )
    return bottle.static_file(filepath, root=locn)


@app.route("/js/<filepath:path>")
def serve_js(filepath):
    log = logging.getLogger("addisonarches.web.serve_js")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/js"
    )
    return bottle.static_file(filepath, root=locn)


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

    bottle.debug(True)
    bottle.TEMPLATES.clear()
    log.debug(bottle.TEMPLATE_PATH)

    log.info("Starting local server...")
    loop = asyncio.get_event_loop()
    fdR, fdW = os.pipe() # TODO: pass to game controller
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(
            addisonarches.game.run,
        )

        app.config.update({
            "args": args,
        })
        bottle.run(app, host="localhost", port=8080)


def run():
    p = addisonarches.game.parser(__doc__)
    args = p.parse_args()
    if args.version:
        sys.stdout.write(__version__ + "\n")
        rv = 0
    else:
        try:
            os.mkdir(args.output)
        except OSError:
            pass
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
