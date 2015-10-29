#!/usr/bin/env python3
# encoding: UTF-8

from collections import namedtuple
from collections import OrderedDict
from functools import singledispatch
import json
import re
import time
import unittest
import uuid

import pkg_resources
import pyratemp

from turberfield.ipc.message import Alert

from addisonarches.web.elements import alert
from addisonarches.web.elements import via
from addisonarches.web.utils import TemplateLoader

#item_macro = PageTemplate(pkg_resources.resource_string(
#    "cloudhands.web.templates", "item_list.pt"))
item_macro = pyratemp.Template(
    filename="items.html.prt",
    loader_class=TemplateLoader,
    data={"unittest": unittest},
)
#nav_macro = PageTemplate(pkg_resources.resource_string(
#    "cloudhands.web.templates", "nav_list.pt"))
#option_macro = PageTemplate(pkg_resources.resource_string(
#    "cloudhands.web.templates", "option_list.pt"))

Ownership = namedtuple("Ownership", ["uuid", "limit", "level"])
SimpleType = namedtuple("SimpleType", ["uuid", "name"])

class TestFundamentals(unittest.TestCase):

    def test_items_macro(self):
        msg = Alert(time.time(), "Time for a test!")
        view = alert(msg)
        print(item_macro(items=[view]))

    def tost_views_without_links_are_not_displayed(self):
        objects = [
            SimpleType(uuid.uuid4().hex, "object-{:03}".format(n))
            for n in range(6)]
        p = TestFundamentals.TestPage()
        for o in objects:
            p.layout.items.push(o)
        rv = item_macro(**dict(p.termination()))
        self.assertNotIn("object-0", rv)


#class TestItemListTemplate(unittest.TestCase):
class TestItemListTemplate:

    class TestPage:

        plan = []

    def test_definition_list_has_class_and_id(self):
        objects = [
            SimpleType(uuid.uuid4().hex, "object-{:03}".format(n))
            for n in range(6)]
        p = TestItemListTemplate.TestPage()
        for o in objects:
            p.layout.items.push(o)
        rv = item_macro(**dict(p.termination()))
        self.assertTrue(re.search('<dl[^>]+class="objectview"', rv))
        self.assertTrue(re.search('<dl[^>]+id="[a-f0-9]{32}"', rv))

    def test_definition_list_contains_public_attributes(self):
        objects = [
            SimpleType(uuid.uuid4().hex, "object-{:03}".format(n))
            for n in range(6)]
        p = TestItemListTemplate.TestPage()
        for o in objects:
            p.layout.items.push(o)
        rv = item_macro(**dict(p.termination()))
        self.assertEqual(6, len(re.findall("<dt[^>]*>name</dt>", rv)))
        self.assertEqual(6, len(re.findall("<dd[^>]*>", rv)))

    def test_list_items_have_aspects(self):
        objects = [
            SimpleType(uuid.uuid4().hex, "object-{:03}".format(n))
            for n in range(6)]
        p = TestItemListTemplate.TestPage()
        for o in objects:
            p.layout.items.push(o)
        rv = item_macro(**dict(p.termination()))
        self.assertEqual(
            6, len(re.findall('<form[^>]+action="/object/[a-f0-9]{32}"', rv)))


#class TestNavListTemplate(unittest.TestCase):
class TestNavListTemplate:

    class TestPage:

        plan = []

    def test_nav_section_exists(self):
        p = TestNavListTemplate.TestPage()
        p.layout.nav.push(SimpleType(uuid.uuid4().hex, "MARMITE"))
        rv = nav_macro(**dict(p.termination()))
        self.assertTrue(re.search(
            '<nav[^>]+class="pure-menu pure-menu-open"', rv))


    def test_menu_contains_each_element(self):
        p = TestNavListTemplate.TestPage()
        p.layout.nav.push(SimpleType(uuid.uuid4().hex, "MARMITE"))
        p.layout.nav.push(SimpleType(uuid.uuid4().hex, "BRANSTON"))
        rv = nav_macro(**dict(p.termination()))
        self.assertEqual(2, rv.count('<a rel="canonical" href="/object/'))
        self.assertIn(">MARMITE</a>", rv)
        self.assertIn(">BRANSTON</a>", rv)


    def test_self_link_shows_visited(self):
        p = TestNavListTemplate.TestPage()
        p.layout.nav.push(SimpleType(uuid.uuid4().hex, "MARMITE"))
        p.layout.nav.push(
            SimpleType(uuid.uuid4().hex, "BRANSTON"), isSelf=True)
        rv = nav_macro(**dict(p.termination()))
        self.assertEqual(1, rv.count('<a rel="canonical" href="/object/'))
        self.assertIn("pure-menu-selected", rv)


class TestOptionListTemplate:
#class TestOptionListTemplate(unittest.TestCase):

    class TestPage:

        plan = []

    def test_definition_list_has_class_and_id(self):
        p = TestItemListTemplate.TestPage()
        p.layout.options.push(Ownership(uuid.uuid4().hex, 256, 18))
        rv = option_macro(**dict(p.termination()))
        self.assertTrue(re.search('<dl[^>]+class="ownershipview"', rv))
        self.assertTrue(re.search('<dl[^>]+id="[a-f0-9]{32}"', rv))

    def test_definition_list_contains_public_attributes(self):
        p = TestItemListTemplate.TestPage()
        p.layout.options.push(Ownership(uuid.uuid4().hex, 256, 18))
        rv = option_macro(**dict(p.termination()))
        self.assertEqual(1, rv.count("<dt>level</dt>"))
        self.assertEqual(1, rv.count("<dd>"))

    def test_list_items_have_aspects(self):
        p = TestItemListTemplate.TestPage()
        p.layout.options.push(Ownership(uuid.uuid4().hex, 256, 18))
        rv = option_macro(**dict(p.termination()))
        self.assertEqual(
            1, len(re.findall('<form[^>]+action="/bag"', rv)))

    def test_print_render(self):
        p = TestItemListTemplate.TestPage()
        p.layout.options.push(Ownership(uuid.uuid4().hex, 256, 18))
        data = dict(p.termination())
        rv = option_macro(**data)
        #print(rv)
        #print(json.dumps(data, cls=TypesEncoder))
