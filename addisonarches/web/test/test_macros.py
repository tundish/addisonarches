#!/usr/bin/env python3
# encoding: UTF-8

from collections import Counter
import re
import time
import unittest
import uuid

import pyratemp

from turberfield.ipc.message import Alert

from addisonarches.game import Game
from addisonarches.utils import group_by_type
from addisonarches.web.elements import alert
from addisonarches.web.elements import item
from addisonarches.web.elements import via
from addisonarches.web.utils import TemplateLoader

item_macro = pyratemp.Template(
    filename="items.html.prt",
    loader_class=TemplateLoader,
    data={"unittest": unittest},
)
nav_macro = pyratemp.Template(
    filename="nav.html.prt",
    loader_class=TemplateLoader,
    data={"unittest": unittest},
)

class TestFundamentals(unittest.TestCase):

    def test_items_macro(self):
        msgs = [
            Game.Item("Compound", "table", "Coffee table", "Lounge", 0),
            Game.Item("Compound", "table", "Coffee table", "Lounge", 0),
            Alert(time.time(), "Time for a test!")
        ]
        groups = group_by_type(msgs)
        totals = Counter(groups[Game.Item])
        views = [typ(i, totals=totals) for typ, i in zip((item, item, alert), msgs)]
        render = item_macro(items=views)
        self.assertTrue(hasattr(views[0], "totals"))
        self.assertTrue(hasattr(views[1], "totals"))
        self.assertTrue(msgs[-1].text in render)

    def test_nav_macro(self):
        msgs = [
            Game.Via(0, "Elevator", "Quickest way down."),
            Game.Via(1, "Ladder", "Slowest way up."),
        ]
        views = [via(i) for i in msgs]
        render = nav_macro(nav=views)
        self.assertEqual(2, render.count("<button"))

class TestOptionListTemplate:

    def test_definition_list_has_class_and_id(self):
        p = TestItemListTemplate.TestPage()
        p.layout.options.push(Ownership(uuid.uuid4().hex, 256, 18))
        rv = option_macro(**dict(p.termination()))
        self.assertTrue(re.search('<dl[^>]+class="ownershipview"', rv))
        self.assertTrue(re.search('<dl[^>]+id="[a-f0-9]{32}"', rv))

    def test_list_items_have_aspects(self):
        p = TestItemListTemplate.TestPage()
        p.layout.options.push(Ownership(uuid.uuid4().hex, 256, 18))
        rv = option_macro(**dict(p.termination()))
        self.assertEqual(
            1, len(re.findall('<form[^>]+action="/bag"', rv)))
