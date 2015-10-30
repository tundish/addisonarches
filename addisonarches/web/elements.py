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

from collections import OrderedDict
import logging
import re
import time

from turberfield.ipc.message import Alert

from addisonarches.business import Buying
from addisonarches.business import Selling
from addisonarches.business import Trader
from addisonarches.game import Game
from addisonarches.game import Clock
from addisonarches.scenario.types import Location
from addisonarches.scenario.types import Character
from addisonarches.web.hateoas import Action
from addisonarches.web.hateoas import Parameter
from addisonarches.web.hateoas import View


def alert(data, session=None, **kwargs):
    try:
        obj = Alert(**data)
    except TypeError:
        obj = data
    return View(obj, actions=OrderedDict([
        ("save", Action(
                name="Save",
                rel="canonical",
                typ="/alerts/{0}",
                ref=(obj.ts,),
                method="post",
                parameters=[
                    Parameter(
                        "text", "hidden",
                        re.compile("[\\w\.! ]{5,64}$"), [],
                        "Alert text is 5 to 64 characters long."),
                    ],
                prompt="OK")),
        ])
    )

def character(data, session=None, **kwargs):
    try:
        obj = Character(**data)
    except TypeError:
        obj = data
    return View(obj, actions={})
 
def drama(data, session=None, **kwargs):
    try:
        obj = Game.Drama(**data)
    except (AttributeError, TypeError):
        obj = data
    rv =  View(obj, actions=OrderedDict())
    if obj.type == "Buying":
        rv.actions["bid"] = Action(
            name="Bid",
            rel="action",
            typ="/{0}/bids",
            ref=(session,),
            method="post",
            parameters=[
                Parameter(
                    "ts", "hidden", re.compile("[0-9.]+"),
                    [time.time()], "Timestamp."),
                Parameter(
                    "value", True, re.compile("[0-9.]+"),
                    [], "Value of bid in £."),
                Parameter(
                    "currency", "hidden", re.compile("[^{}/]+"),
                    ["£"], "Bidding currency."),
                ],
            prompt="OK")
    return rv
 
 
def item(data, session=None, totals={}, **kwargs):
    types = {"owner": int}
    try:
        obj = Game.Item(**{k: types.get(k, str)(v) for k, v in data.items()})
    except (AttributeError, TypeError):
        obj = data
    rv =  View(obj, actions=OrderedDict([
        ("buy", Action(
                name="Buy",
                rel="action",
                typ="/{0}/buying",
                ref=(session,),
                method="post",
                parameters=[
                    Parameter(
                        k, "hidden", re.compile("[^{}/]+"),
                        [getattr(obj, k)], "Data field")
                    for k in obj._fields
                    ],
                prompt="OK")),
        ])
    )
    rv.totals = totals
    return rv
 
def patter(data, session=None, **kwargs):
    try:
        obj = Trader.Patter(**data)
    except TypeError:
        obj = data
    return View(obj, actions={})
 
def tally(data, session=None, **kwargs):
    try:
        obj = Game.Tally(**data)
    except TypeError:
        obj = data
    return View(obj, actions={})
 
def tick(data, session=None, **kwargs):
    try:
        obj = Clock.Tick(**data)
    except TypeError:
        obj = data
    return View(obj, actions={})
 
def via(data, session=None, **kwargs):
    log = logging.getLogger("addisonarches.web")
    types = {"id": int}
    try:
        obj = Game.Via(**{k: types.get(k, str)(v) for k, v in data.items()})
    except (AttributeError, TypeError):
        obj = data
    return View(obj, actions=OrderedDict([
        ("go", Action(
                name="_hidden",
                rel="canonical",
                typ="/{0}/vias",
                ref=(session,),
                method="post",
                parameters=[
                    Parameter(
                        "id", True, re.compile("[0-9]+"),
                        [obj.id], "Index of available vias."),
                    Parameter(
                        "name", True, re.compile("[^{}/]+"),
                        [obj.name], "Name of via."),
                    Parameter(
                        "tip", True, re.compile("[^{}/]+"),
                        [obj.tip], "Go to {}.".format(obj.name)),
                    ],
                prompt="OK")),
        ])
    )

def login(data, **kwargs):
    try:
        obj = User(**data)
    except IndexError:
        obj = data
    return View(obj, actions=OrderedDict([
        ("save", Action(
                name="User login",
                rel="login",
                typ="/login/{}",
                ref="0987654321",
                method="post",
                parameters=[
                    Parameter(
                        "username", True, re.compile("\\w{8,10}$"),
                        [],
                        """
                        User names are 8 to 10 characters long.
                        """),
                    Parameter(
                        "password", True, re.compile(
                            "^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z])"
                            "(?=.*[^a-zA-Z0-9])"
                            "(?!.*\\s).{8,20}$"
                        ), [],
                        """
                        Passwords are between 8 and 20 characters in length.
                        They must contain:
                        <ul>
                        <li>at least one lowercase letter</li>
                        <li>at least one uppercase letter</li>
                        <li>at least one numeric digit</li>
                        <li>at least one special character</li>
                        </ul>
                        They cannot contain whitespace.
                        """),
                    ],
                prompt="OK")),
        ])
    )
