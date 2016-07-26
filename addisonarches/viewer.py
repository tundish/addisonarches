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

# TODO: Move to turberfield-utils

from addisonarches.utils import plugin_interface

import argparse
import docutils.parsers.rst
import docutils.utils
import pkg_resources
import sys

__doc__ = """
WIP
"""

settings=argparse.Namespace(
    debug = False, error_encoding="utf-8",
    error_encoding_error_handler="backslashreplace", halt_level=4,
    id_prefix="", language_code="en",
    pep_references=1,
    report_level=2, rfc_references=1, tab_width=4,
    warning_stream=sys.stderr
)

def sources(args):
    menu = list(dict(plugin_interface("turberfield.interfaces.scenes")).values())
    for scenes in menu:
        for path in scenes.paths:
            name = "{0}:{1}".format(scenes.pkg, path)
            text = pkg_resources.resource_string(scenes.pkg, path).decode("utf-8")
            yield name, text
    if args.infile:
        name = args.infile.name
        text = args.infile.read()
        yield name, text

def main(args):
    parser = docutils.parsers.rst.Parser()
    for name, text in sources(args):
        doc = docutils.utils.new_document(name, settings)
        parser.parse(text, doc)
        print(doc)

def parser(description=__doc__):
    rv =  argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    rv.add_argument("infile", nargs="?", type=argparse.FileType("r"),
    default=sys.stdin)
    return rv

def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
