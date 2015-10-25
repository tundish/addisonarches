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

import unittest
from unittest.mock import Mock

from addisonarches.web.services import Service

class RegisterTests(unittest.TestCase):

    def test_route_with_regex(self):

        class UsesRegex(Service):

            def css_path_get(self, request):
                pass

            def session_get(self, request):
                pass

        app = Mock()
        svc = UsesRegex(None)
        rv = dict(list(svc._register(
            app,
            "/css/{path:[^{}]+}",
            "/{session:[a-z0-9]{32}}",
        )))
        self.assertEqual(rv["css_path_get"], svc.css_path_get)
        self.assertEqual(rv["session_get"], svc.session_get)
