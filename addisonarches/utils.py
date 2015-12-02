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
from turberfield.ipc.message import load
from turberfield.ipc.message import registry
from turberfield.utils.misc import type_dict

#from addisonarches.business import Trader
#from addisonarches.game import Clock
#from addisonarches.game import Game
#from addisonarches.game import Persistent
#from addisonarches.scenario import Location
#from addisonarches.scenario.types import Character

# TODO: Each class definition updates registry
#registry.update(
#    type_dict(
#        Alert, Character, Clock.Tick,
#        Game.Drama, Game.Item, Game.Player, Game.Tally, Game.Via,
#        Location, Trader.Patter
#    )
#)

"""
def send(obj, stream=sys.stdout):
    msg = dict(vars(obj).items())
    msg["_type"] = type(obj).__name__
    try:
        pprint(msg, stream=stream, compact=True, width=sys.maxsize)
    except TypeError:  # 'compact' is new in Python 3.4
        pprint(msg, stream=stream, width=sys.maxsize)
    finally:
        stream.flush()
    return stream

def receive(data):
    types = {i.__name__: i for i in (Game.Player,)}
    payload = ast.literal_eval(data.decode("utf-8").rstrip("\n"))
    return types.get(payload.pop("_type", None), dict)(**payload)
"""

def get_objects(path, types=registry.values()):
    path = os.path.join(*path)
    if not os.path.isfile(path):
        return []
    with open(path, 'r') as content:
        data = rson2objs(content.read(), types)
        return data

def rson2objs(text, types):
    """
    Read an RSON string and return a sequence of data objects.
    """
    #which = {i.__name__: i for i in types}
    which = types
    try:
        things = rson.loads(text)
        things = things if isinstance(things, list) else [things]
    except IndexError:
        things = []
    return [which.get(i.pop("_type", None), dict)(**i) for i in things]

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

