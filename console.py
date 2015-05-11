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

import cmd
from collections import namedtuple
import datetime
import itertools


class Console(cmd.Cmd):
    clock = (
        t for t in (
            datetime.datetime(year=2015, month=5, day=11) +
            datetime.timedelta(seconds=i)
            for i in itertools.count(0, 30 * 60))
        if 8 <= t.hour <= 19)
    prompt = "{:%A %H:%M} > ".format(next(clock))

    def postcmd(self, stop, line):
        self.prompt = "{:%A %H:%M} > ".format(next(self.clock))
        return stop

if __name__ == "__main__":
    console = Console()
    console.cmdloop()
