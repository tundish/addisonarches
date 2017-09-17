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


from collections import defaultdict
from collections import namedtuple

from addisonarches.fuzzywuzzy import process

Reply = namedtuple("Reply", ["text", "action"])
Trigger = namedtuple("Trigger", ["gist", "variants"])

phrases = {i.gist: i for i in [
    Trigger(
        "Hello", ("hi", "hello", "greetings!")
    ),
    Trigger(
        "want food",
        ("i want food", "i'm hungry")
    )
]
}


class Script:

    def __init__(self):
        self.phrases = {}
        self.replies = defaultdict(list)

    def register(self, trigger, reply):
        for v in trigger.variants:
            self.phrases[v] = trigger
        self.replies[trigger].append(reply)

    def prompt(self, line):
        hits = process.extract(line, self.phrases.keys())
        return ((reply, score) for phrase, score in hits
                for reply in self.replies[self.phrases[phrase]])


