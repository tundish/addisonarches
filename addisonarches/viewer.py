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

from addisonarches.direction.directives import RoleDirective
from addisonarches.utils import plugin_interface

import argparse
import docutils
import docutils.utils
import pkg_resources
import sys

__doc__ = """
WIP
"""

class Scenes:

    settings=argparse.Namespace(
        debug = False, error_encoding="utf-8",
        error_encoding_error_handler="backslashreplace", halt_level=4,
        auto_id_prefix="", id_prefix="", language_code="en",
        pep_references=1,
        report_level=2, rfc_references=1, tab_width=4,
        warning_stream=sys.stderr
    )

    def __init__(self):
        docutils.parsers.rst.directives.register_directive(
            "part", RoleDirective
        )

    def read(self, text, name=None):
        doc = docutils.utils.new_document(name, Scenes.settings)
        parser = docutils.parsers.rst.Parser()
        parser.parse(text, doc)
        return doc.children

def sources(args):
    menu = list(dict(plugin_interface("turberfield.interfaces.scenes")).values())
    for scenes in menu:
        for path in scenes.paths:
            name = "{0}:{1}".format(scenes.pkg, path)
            text = pkg_resources.resource_string(scenes.pkg, path).decode("utf-8")
            yield name, text
    if not menu:
        name = args.infile.name
        text = args.infile.read()
        yield name, text

def main(args):
    scenes = Scenes()
    for name, text in sources(args):
        #doc = scenes.read(text, name=name)
        doc = scenes.read(text)
        print(doc)
        for node in doc.children:
            print(type(node))
            if isinstance(node, ParsedLiteral):
                print(node)

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
