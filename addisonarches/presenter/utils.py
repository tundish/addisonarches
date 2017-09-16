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

import functools

import pkg_resources
import pyratemp


class TemplateLoader(pyratemp.LoaderFile):

    def __init__(self, *args, encoding="utf=8", **kwargs):
        path = pkg_resources.resource_filename("addisonarches.presenter", "templates")
        super().__init__(path, encoding, **kwargs)

    @functools.lru_cache(maxsize=16)
    def load(self, name):
        return pkg_resources.resource_string(
            "addisonarches.presenter",
            "templates/{}".format(name)
        ).decode(self.encoding)

def authenticated_userid(request):
    return "someone@somewhere.net"
