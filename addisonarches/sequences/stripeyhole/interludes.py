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
import sys

# TODO: move to turberfield.dialogue
from addisonarches.sequences.directives import RoleDirective

import docutils

# TODO: SceneSequence
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
