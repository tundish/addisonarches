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


import ast
import logging
import os.path
from pprint import pprint
import sys


DFLT_LOCN = os.path.expanduser(os.path.join("~", ".addisonarches"))
DFLT_PORT = 8080

def add_common_options(parser):
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

def send(obj, stream=sys.stdout):
    msg = vars(obj)
    msg["_type"] = type(obj).__name__
    try:
        pprint(msg, stream=stream, compact=True, width=sys.maxsize)
    except TypeError:  # 'compact' is new in Python 3.4
        pprint(msg, stream=stream, width=sys.maxsize)
    finally:
        stream.flush()

def receive(stream):
    payload = stream.readline().rstrip("\n")
    bits =  ast.literal_eval(payload)
    types = {i.__name__: i for i in (BlogPost,)}
    return [types.get(i.pop("_type", None), dict)(**i) for i in things]

