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

import time
import unittest

from aiohttp import MultiDict
from turberfield.ipc.message import Alert

from addisonarches.web.elements import alert


class AlertTests(unittest.TestCase):

    def test_alert_from_msg(self):
        msg = Alert(time.time(), "There was a bang!")
        view = alert(msg)
        self.assertIs(msg, view.obj)
        self.assertEqual(1, len(view.actions))
        problems = view.rejects("save")
        self.assertFalse(problems)

    def test_alert_from_multidict(self):
        msg = Alert(time.time(), "There was a bang!")
        data = MultiDict(**vars(msg))
        view = alert(data)
        self.assertEqual(msg, view.obj)
        self.assertEqual(1, len(view.actions))
        problems = view.rejects("save")
        self.assertFalse(problems)

    def test_alert_from_bad_multidict(self):
        msg = Alert(time.time(), "There was a b*ng!")
        data = MultiDict(**vars(msg))
        view = alert(data)
        self.assertEqual(msg, view.obj)
        self.assertEqual(1, len(view.actions))
        problems = view.rejects("save")
        self.assertTrue(problems)
