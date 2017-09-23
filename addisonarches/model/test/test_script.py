#!/usr/bin/env python3.4
#   encoding: UTF-8

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

import unittest

from addisonarches.model.script import phrases
from addisonarches.model.script import Trigger
from addisonarches.model.script import Reply
from addisonarches.model.script import Script

class FuzzTests(unittest.TestCase):

    def test_i_am(self):
        script = Script()
        im = Trigger("I am", ("i am", "i'm"))
        imnot = Trigger("I am not", ("i am not", "i'm not"))
        right = Reply("Correct reply", None)
        wrong = Reply("Incorrect reply", None)
        script.register(im, right)
        script.register(imnot, wrong)
        rv, score = next(script.prompt("I'm"))
        self.assertIs(right, rv)
        

class NewPlayerTests(unittest.TestCase):

    def test_null_reply(self):
        script = Script()
        r = Reply("Correct reply", None)
        script.register(phrases["Hello"], r)
        rv, score = next(script.prompt("Goodbye"))
        self.assertLessEqual(score, 50)

    def test_say_hello(self):
        script = Script()
        script.register(
            phrases["Hello"],
            Reply("And hello to you", None))
        rv, score = next(script.prompt("Hi"))
        self.assertEqual("and hello to you", rv.text.lower())

    def test_want_food(self): 
        script = Script()
        r = Reply("Correct reply", None)
        w = Reply("Incorrect reply", None)
        script.register(phrases["want food"], r)
        script.register(phrases["Hello"], w)
        self.assertIs(r, next(script.prompt("I want food"))[0])
        self.assertIs(r, next(script.prompt("I'm hungry"))[0])
        self.assertIs(r, next(script.prompt("I am hungry"))[0])
        self.assertIs(r, next(script.prompt("Have you got any food?"))[0])
        # Unexpected consequences...
        rv, score = next(script.prompt("Do you want any food?"))
        self.assertGreaterEqual(score, 75)
        rv, score = next(script.prompt("Are you hungry?"))
        self.assertGreaterEqual(score, 70)
