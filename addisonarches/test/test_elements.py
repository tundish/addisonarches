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

import datetime
from decimal import Decimal
import itertools
import unittest

from addisonarches.elements import Action
from addisonarches.elements import Parameter

"""
http://www.w3.org/TR/web-animations/

* Global clock is elapsed game time for player in milliseconds?
* Global clock is number of page loads for player?
* Consider turberfield.dynamics.simulation.Simulation as Animation?

* CSS will-change property
* -prefix-free.js

"""

# TODO: separate module for timeline. Capture user visits as global
# clock?

class Timeline:

    @classmethod
    def reset(cls):
        cls._value = start = datetime.datetime(
            year=2015, month=5, day=11)
        cls._source = (
            t for t in (
                start +
                datetime.timedelta(seconds=i)
                for i in itertools.islice(
                    itertools.count(0, 30 * 60),
                    7 * 24 * 60 // 30)
                )
            if 8 <= t.hour <= 19)
        
    @classmethod
    def tick(cls):
        try:
            cls._value = next(cls._source)
        except AttributeError:
            cls.reset()
        
    def __init__(self, offset=0):
        self.delta = datetime.timedelta(milliseconds=offset)

    @property
    def value(self):
        try:
            return Timeline._value + self.delta
        except AttributeError:
            Timeline.reset()
            return Timeline._value + self.delta

class Player:

    def __init__(self, timeline, start, delay, rate=1.0):
        self.timeline = timeline
        self.start = start
        self.delay = delay
        self.rate = rate
        self.hold = None

    def current_time(self):
        return (
            self.hold or
            (self.timeline.value - self.start) * self.rate
        )

class AnimationsTester(unittest.TestCase):

    def test_shared_timeline(self):
        tList = [
            Timeline(0),
            Timeline(0),
        ]
        self.assertEqual(tList[0].value, tList[1].value)

        prev = tList[0].value
        Timeline.tick()

        # First tick of the morning spans 8 hours
        self.assertEqual(60 * 60 * 8, (tList[0].value - prev).seconds)
        self.assertEqual(tList[0].value, tList[1].value)

        prev = tList[0].value
        Timeline.tick()

        # Regular tick is half an hour
        self.assertEqual(30 * 60, (tList[0].value - prev).seconds)
        self.assertEqual(tList[0].value, tList[1].value)

    def test_current_time(self):
        tL = Timeline(0)
        self.assertEqual(2015, tL.value.year)
        self.assertEqual(0, tL.value.second)
        p = Player(tL, 0, 0)
        self.assertIs(None, p.hold)
        
