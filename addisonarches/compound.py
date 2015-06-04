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

from collections import Counter
from collections import deque
import re

class Memory:

    def __init__(self, *args, **kwargs):
        iterable = kwargs.pop("iterable", [])
        maxlen = kwargs.pop("maxlen", None)
        self.memory = deque(iterable, maxlen)

class Compound:

    @staticmethod
    def recipe():
        raise NotImplementedError

    @classmethod
    def requirements(class_):
        for k, v in class_.recipe().items():
            try:
                yield from k.requirements()
            except AttributeError:
                yield (k, getattr(v, "value", v))
        
    @classmethod
    def build(class_, inventory:Counter, *args, **kwargs):
        recipe = Counter(
            {k: getattr(v, "value", v) for k, v in class_.recipe().items()}
        )
        components = Counter()
        for obj, n in inventory.copy().items():
            typ = type(obj)
            used = min(n, recipe[typ])
            recipe[typ] -= used
            components[obj] += used

        if sum(recipe.values()):
            return None
        else:
            inventory.subtract(components) 
            return class_(components, *args, **kwargs)

    @property
    def description(self):
        return self.__doc__.strip()

    @property
    def label(self):
        return " ".join(i.lower() for i in re.split(
            "([A-Z][^A-Z]*)", self.__class__.__name__) if i)

    @property
    def volume(self):
        return sum(getattr(i, "volume", 0) for i in self.components)

    def __init__(self, components, *args, **kwargs):
        self.components = components
        super().__init__(*args, **kwargs)
