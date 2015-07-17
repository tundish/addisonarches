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

import io
import unittest

from addisonarches.cli import send
from addisonarches.cli import receive
from addisonarches.game import Game

class CLITests(unittest.TestCase):

    user = "someone@somewhere.net"

    @staticmethod
    def transmit(stringio):
        return stringio.getvalue().encode("utf-8")

    def test_message_streaming(self):
        stream = io.StringIO()
        obj = Game.Player(CLITests.user, "Player 1")
        content = CLITests.transmit(send(obj, stream))
        self.assertEqual(obj, receive(content))
