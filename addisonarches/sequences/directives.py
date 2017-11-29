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


from collections import namedtuple
import docutils.parsers.rst

class RoleDirective(docutils.parsers.rst.Directive):

    """
    http://docutils.sourceforge.net/docutils/parsers/rst/directives/parts.py
    """

    Node = namedtuple("Role", ["name", "note", "relationships"])
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = True

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


