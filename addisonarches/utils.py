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
from collections import namedtuple
import itertools
import os.path
import pkg_resources
from pprint import pprint
import sys

import rson

from turberfield.ipc.message import Alert
from turberfield.utils.assembly import Assembly


# TODO: Move to turberfield-utils
def plugin_interface(key="turberfield.interfaces"):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)


def get_objects(path):
    path = os.path.join(*path)
    if not os.path.isfile(path):
        return []
    with open(path, 'r') as content:
        data = rson2objs(content.read())
        return data

def rson2objs(text):
    """
    Read an RSON string and return a sequence of data objects.
    """
    if not text:
        return []
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
