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
import contextlib
import os
import locale
import logging
import sys

import addisonarches.console
import addisonarches.web.main

DFLT_LOCN = os.path.expanduser(os.path.join("~", ".addisonarches"))


__doc__ = """
Main entry point for Addison Arches game.
"""

def parsers(description=__doc__):
    parser = argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    parser.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    parser.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    parser.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    parser.add_argument(
        "--output", default=DFLT_LOCN,
        help="path to output directory [{}]".format(DFLT_LOCN))

    subparsers = parser.add_subparsers(
        dest="command",
        help="Commands:",
    )
    return (parser, subparsers)

def add_console_command_parser(subparsers):
    rv = subparsers.add_parser(
        "console", help="Play the game from a text console.",
        description="", epilog="other commands: web"
    )
    rv.usage = rv.format_usage().replace("usage:", "").replace(
        "console", "\n\naddisonarches [OPTIONS] console")
    return rv
 
def add_web_command_parser(subparsers):
    rv = subparsers.add_parser(
        "web", help="Play the game over a web interface.",
        description="", epilog="other commands: console"
    )
    rv.add_argument(
        "--host", required=False,
        help="Specify the name of the remote host")
    rv.add_argument(
        "--port", type=int, required=False,
        help="Specify the port number to the host")
    rv.add_argument(
        "--user", required=False,
        help="Specify the user login on the host")
    rv.add_argument(
        "--python", required=False,
        help="Specify the Python executable on the remote host")
    rv.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
    rv.usage = rv.format_usage().replace("usage:", "").replace(
        "web", "\n\naddisonarches [OPTIONS] web")
    return rv

def subprocess_queue_factory(queue, loop):

    def pipe_data_received(self, fd, data):
        if fd == 1:
            name = 'stdout'
        elif fd == 2:
            name = 'stderr'
        text = data.decode(locale.getpreferredencoding(False))
        print('Received from {}: {}'.format(name, text.strip()))

    def process_exited(self):
        self.loop.stop()

    return type(
        "SubprocessQueue",
        (asyncio.SubprocessProtocol,),
        dict(
            loop=loop,
            pipe_data_received=pipe_data_received,
            process_exited=process_exited,
            queue=queue
        )
    )

def main(args):
    if args.command == "console":
        rv = addisonarches.console.main(args)
    elif args.command == "web":
        rv = 0
        if os.name == "nt":
            # On Windows, the ProactorEventLoop is necessary to listen on pipes
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        with contextlib.closing(loop):
            # This will only connect to the process
            transport = loop.run_until_complete(
                loop.subprocess_exec(
                    subprocess_queue_factory(None, loop),
                    sys.executable,
                    '-c', 'print(\'Hello async world!\')')
            )[0]
            # Wait until process has finished
            loop.run_forever()
            print('Program exited with: {}'.format(transport.get_returncode()))
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
