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

from collections import deque
from collections import namedtuple
import datetime
import random
import statistics
import warnings

from tallywallet.common.finance import Note
from tallywallet.common.finance import value_series

from turberfield.utils.assembly import Assembly

fields = ["ts", "value", "currency"]
Ask = namedtuple("Ask", fields)
Bid = namedtuple("Bid", fields)
Valuation = namedtuple("Valuation", fields)


class ValueBook(dict):

    @staticmethod
    def approve(series, offer:set([Ask, Bid]), **kwargs):
        sd = statistics.pstdev(i.value for i in series)
        estimate = ValueBook.estimate(series, **kwargs)
        if isinstance(offer, Ask):
            return (offer.value < estimate.value
                    or offer.value - estimate.value < sd / 2)
        elif isinstance(offer, Bid):
            return (offer.value > estimate.value
                    or estimate.value - offer.value < sd / 2)
        else:
            raise NotImplementedError

    @staticmethod
    def estimate(series, ts=None):
        currencies = {i.currency for i in series}
        if len(currencies) > 1:
            warnings.warn("Mixed currencies ({})".format(currencies))
            return None
        else:
            return Valuation(
                None,
                statistics.median(i.value for i in series),
                currencies.pop()
            )

    def commit(self, commodity, obj:set([Ask, Bid, Note])):
        if isinstance(obj, Note):
            series = super().setdefault(
                commodity,
                deque([], maxlen=obj.term // obj.period)
            )
            series.extend(
                [Valuation(*i, currency=obj.currency)
                 for i in value_series(**obj._asdict())]
            )
        elif isinstance(obj, (Ask, Bid)):
            series = self[commodity]
            series.append(obj)
        else:
            raise NotImplementedError

        return self.estimate(series)

    def consider(self, commodity, offer:set([Ask, Bid]), constraint=1.0):
        estimate = self.estimate(self[commodity])
        if isinstance(offer, Ask):
            if offer.value < estimate.value or random.random() >= constraint:
                return self.commit(commodity, offer)
            else:
                return estimate
        elif isinstance(offer, Bid):
            if offer.value > estimate.value or random.random() <= constraint:
                return self.commit(commodity, offer)
            else:
                return estimate
        else:
            raise NotImplementedError

    def setdefault(self, key, default=None):
        raise NotImplementedError

    def update(self, other):
        raise NotImplementedError

Assembly.register(Ask, Bid, Note, Valuation)
