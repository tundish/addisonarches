#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import abc
from collections import defaultdict
from collections import namedtuple
import enum
import unittest
import uuid

from turberfield.machina.stage import Stage

NPC = namedtuple("NPC", ["uuid", "name"])
Player = namedtuple("Player", ["uuid", "name"])


@enum.unique
class Commodity(enum.Enum):
    COIN = "coin"
    SCRP = "scrip"


@enum.unique
class TradePosition(enum.Enum):

    buying = "buying"
    selling = "selling"

Role = namedtuple("Role", ["name", "description"])

Applause = namedtuple("Applause", ["todo"])
Dialogue = namedtuple("Dialogue", ["todo"])

Location = namedtuple("Location", ["lat", "long"])


class Scene(metaclass=abc.ABCMeta):

    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def casting(self):
        pass


class PayingOff(Scene):
    """
    This scene can be played every time a worker in a scrip system wants
    to cash in his tokens for coin.
    """

    sellout = Role("sellout", None)
    broker = Role("broker", None)

    @property
    def casting(self):
        return {
            frozenset([
                (Commodity.COIN, frozenset([TradePosition.buying])),
                (Commodity.SCRP, frozenset([TradePosition.selling]))
            ]): [PayingOff.sellout],
            frozenset([
                (Commodity.COIN, frozenset([TradePosition.selling])),
                (Commodity.SCRP, frozenset([TradePosition.buying]))
            ]): [PayingOff.broker],
        }

    def __call__(self, sellout, broker):
        yield Dialogue(None)
        yield Applause(None)

    def __enter__(self):
        # Lock actors
        # Set up stage
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Unlock actors
        return False

characters = {
    NPC(uuid.uuid4().hex, "worker #01"): {
        Commodity.COIN: [TradePosition.buying],
        Commodity.SCRP: [TradePosition.selling],
    },
    NPC(uuid.uuid4().hex, "worker #02"): {},
    NPC(uuid.uuid4().hex, "worker #03"): {},
    NPC(uuid.uuid4().hex, "worker #04"): {},
    NPC(uuid.uuid4().hex, "worker #05"): {},
    NPC(uuid.uuid4().hex, "worker #06"): {},
    NPC(uuid.uuid4().hex, "worker #07"): {},
    Player(uuid.uuid4().hex, "Alice"): {},
    Player(uuid.uuid4().hex, "Bob"): {},
    Player(uuid.uuid4().hex, "Carl"): {},
}


class PrototypeCasting(unittest.TestCase):

    def test_role_discovery(self):
        scene = PayingOff()
        self.assertIsInstance(scene.casting, dict)
        attitude = defaultdict(set)
        for actor, dramas in characters.items():
            for counterparty, relationships in dramas.items():
                attitude[actor].add(
                    (counterparty, frozenset(relationships))
                )
        print({frozenset(v): k for k, v in attitude.items()})

        for dramas, role in scene.casting.items():
            for counterparty, relationships in dramas:
                for rel in relationships:
                    print(rel)

    def test_scene_discovery(self):
        stage = Stage(
            id=uuid.uuid4().hex,
            scenes=[PayingOff])

    def test_playing_the_scene(self):
        scene = PayingOff
        with scene() as performance:
            for n, msg in enumerate(performance(
                sellout=None, broker=None)
            ):
                self.assertTrue(msg)
            self.assertTrue(n)
