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


import asyncio
from collections import OrderedDict
import logging
import os
import time
import urllib.parse

import aiohttp.web
import pkg_resources
import pyratemp

from addisonarches import __version__
from addisonarches.web.utils import TemplateLoader

class Service:

    verbs = ("get", "head", "options", "post", "put", "delete", "trace", "connect", "patch")

    def __init__(self, app, **kwargs):
        self.config = kwargs

    def _register(self, app, *args):
        table = str.maketrans("/", "_", "{}[]^+*:.?()$")
        for path in args:
            base = urllib.parse.urlparse(path).path.strip("/").translate(table)
            for verb in Service.verbs:
                name = "{}_{}".format(base, verb)
                try:
                    fn = getattr(self, name)
                except AttributeError:
                    pass
                else:
                    app.router.add_route(verb, path, fn, name=name)
                    yield (name, fn)
                

class Assets(Service):

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.routes = dict(list(self._register(
            app,
            "/audio/{path}",
            "/css/{path:[^{}]+}",
            "/img/{path}",
            "/js/{path}"
        )))

    @asyncio.coroutine
    def audio_path_get(self, request):
        path = request.match_info["path"]
        if os.sep in path:
            return aiohttp.web.HTTPForbidden()
        else:
            data = pkg_resources.resource_string(
                "addisonarches.web",
                "static/audio/{}".format(path)
            )
            return aiohttp.web.Response(
                body=data,
                content_type="audio/wav"
            )

    @asyncio.coroutine
    def css_path_get(self, request):
        path = request.match_info["path"]
        if ".." in path:
            return aiohttp.web.HTTPForbidden()
        else:
            data = pkg_resources.resource_string(
                "addisonarches.web",
                "static/css/{}".format(path)
            )
            return aiohttp.web.Response(
                body=data,
                content_type="text/css"
            )

    @asyncio.coroutine
    def img_path_get(self, request):
        path = request.match_info["path"]
        ext = os.path.splitext(path)[1]
        if not ext or os.sep in path:
            return aiohttp.web.HTTPForbidden()
        else:
            data = pkg_resources.resource_string(
                "addisonarches.web",
                "static/img/{}".format(path)
            )
            cType = {
                "jpg": "image/jpeg",
                "png": "image/png",
            }.get(ext, "application/octet-stream")
            return aiohttp.web.Response(
                body=data,
                content_type=cType
            )

    @asyncio.coroutine
    def js_path_get(self, request):
        path = request.match_info["path"]
        if os.sep in path:
            return aiohttp.web.HTTPForbidden()
        else:
            data = pkg_resources.resource_string(
                "addisonarches.web",
                "static/js/{}".format(path)
            )
            return aiohttp.web.Response(
                body=data,
                content_type="text/javascript"
            )

class Transitions(Service):

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.routes = dict(list(self._register(app, "/titles")))

    def titles(self, items=[]):
        return {
            "info": {
                "args": self.config.get("args"),
                "interval": 200,
                "time": "{:.1f}".format(time.time()),
                "title": "Addison Arches {}".format(__version__),
                "version": __version__
            },
            "items": OrderedDict([(str(id(i)), i) for i in items]),
            
        }

    @asyncio.coroutine
    def titles_get(self, request):
        tmplt = pyratemp.Template(filename="titles.prt", loader_class=TemplateLoader)
        return aiohttp.web.Response(
            content_type="text/html",
            text=tmplt(**self.titles())
        )