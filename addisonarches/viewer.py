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
import docutils
import docutils.parsers.rst
from docutils.parsers.rst.directives.body import ParsedLiteral
import docutils.utils
import pkg_resources
import sys

__doc__ = """
WIP
"""

class ActorDirective(docutils.parsers.rst.Directive):

    """
    http://docutils.sourceforge.net/docutils/parsers/rst/directives/parts.py
    """

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = True
    node_class = ParsedLiteral

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        # Create the admonition node, to be populated by `nested_parse`.
        text = '\n'.join(self.content)
        text_nodes, messages = self.state.inline_text(text, self.lineno)
        node = docutils.nodes.literal_block(text, '', *text_nodes, **self.options)
        node.line = self.content_offset + 1
        self.add_name(node)
        return [node] + messages
        kwargs = {
            i: getattr(self, i, None)
            for i in (
                "name", "arguments", "options", "content", "lineno", "content_offset",
                "block_text", "state", "state_machine"
            )
        }
        dialogueNode = self.node_class(**kwargs)
        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset, dialogueNode)
        return [dialogueNode]

docutils.parsers.rst.directives.register_directive("actor", ActorDirective)


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
