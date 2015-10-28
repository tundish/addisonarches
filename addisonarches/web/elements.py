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
import re

from turberfield.ipc.message import Alert

from addisonarches.web.hateoas import Action
from addisonarches.web.hateoas import Parameter


def alert(data):
    try:
        obj = Alert(**data)
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

def login(data):
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
