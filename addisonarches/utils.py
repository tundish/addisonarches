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


import ast
from collections import defaultdict
import itertools
import os.path
from pprint import pprint
import sys

import rson

from turberfield.ipc.message import Alert
from turberfield.utils.assembly import Assembly


def get_objects(path):
    path = os.path.join(*path)
    if not os.path.isfile(path):
        return []
    with open(path, 'r') as content:
        data = rson2objs(content.read(), types)
        return data

def rson2objs(text):
    """
    Read an RSON string and return a sequence of data objects.
    """
    things = rson.loads(text)
    things = things if isinstance(things, list) else [things]
    return [Assembly.object_hook(i) for i in things]

def group_by_type(items):
    return defaultdict(list,
        {k: list(v) for k, v in itertools.groupby(items, key=type)}
    )

def query_object_chain(items, key, value=None, group="", obj=None):
    """
    Search a sequence of items for attribute values or find defaults from
    previous ones.

    """
    if obj is None:
        chain = reversed(items)
    else:
        chain = (
            obj,
            next((i for i in items if isinstance(i, type(obj))), None)
        )
    if not group:
        return next(
            (item
            for item in chain
            if value is None and hasattr(item, key)
            or value is not None and getattr(item, key, None) == value),
            None
        )
    else:
        return next(
            (item
            for item in chain
            for p in getattr(item, group, [])
            if value is None and hasattr(item, key)
            or value is not None and getattr(p, key, None) == value),
            None
        )

