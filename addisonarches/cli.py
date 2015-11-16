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
import logging
import os.path

from turberfield.ipc.cli import add_common_options

DFLT_LOCN = os.path.expanduser(os.path.join("~", ".addisonarches"))
DFLT_PORT = 8080

def add_game_options(parser):
    parser.add_argument(
        "--output", default=DFLT_LOCN,
        help="path to output directory [{}]".format(DFLT_LOCN))
    return parser


def add_web_options(parser):
    parser.add_argument(
        "--host", default="localhost",
        help="Specify the name of the remote host")
    parser.add_argument(
        "--port", type=int, default=DFLT_PORT,
        help="Specify the port number [{}] to the host".format(DFLT_PORT))
    parser.add_argument(
        "--user", required=False,
        help="Specify the user login on the host")
    parser.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
    return parser


def parsers(description=__doc__):
    parser =  argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    parser = add_common_options(parser)
    parser = add_game_options(parser)
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
    rv = add_web_options(rv)
    rv.usage = rv.format_usage().replace("usage:", "").replace(
        "web", "\n\naddisonarches [OPTIONS] web")
    return rv
