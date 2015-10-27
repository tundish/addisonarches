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
import functools

Action = namedtuple(
    "Action", ["name", "rel", "typ", "ref", "method", "parameters", "prompt"])
Parameter = namedtuple("Parameter", ["name", "required", "regex", "values", "tip"])


class Validating:

    @property
    def parameters(self):
        return []

    @property
    def invalid(self):
        missing = [i for i in self.parameters
                   if i.required and i.name not in self]
        missing = missing or [
            i for i in self.parameters if i.name in self
            and i.values and self[i.name] not in i.values]
        missing = missing or [
            i for i in self.parameters
            if i.name in self and not i.regex.match(self[i.name])]
        return missing
