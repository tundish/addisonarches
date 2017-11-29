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
from collections import Counter
from collections import OrderedDict
import logging
import os
import subprocess
import sys
import time
import urllib.parse
import uuid

import aiohttp.web
import pkg_resources
import pyratemp
from turberfield.ipc.message import Address
from turberfield.ipc.message import Alert
from turberfield.ipc.message import parcel

from addisonarches import __version__
from addisonarches.model.business import Buying
from addisonarches.model.business import Selling
from addisonarches.model.business import Trader

from addisonarches.model.game import Clock
from addisonarches.model.game import Game
from addisonarches.model.game import Persistent
from addisonarches.scenario.types import Location
from addisonarches.scenario.types import Character

from addisonarches.utils import get_objects
from addisonarches.utils import group_by_type

from addisonarches.presenter.elements import alert
from addisonarches.presenter.elements import ask
from addisonarches.presenter.elements import bid
from addisonarches.presenter.elements import character
from addisonarches.presenter.elements import dialogue
from addisonarches.presenter.elements import drama
from addisonarches.presenter.elements import item
from addisonarches.presenter.elements import patter
from addisonarches.presenter.elements import tally
from addisonarches.presenter.elements import tick
from addisonarches.presenter.elements import via
from addisonarches.presenter.utils import TemplateLoader

APP_NAME = "addisonarches.web.services"

class Service:

    verbs = ("get", "head", "options", "post", "put", "delete", "trace", "connect", "patch")

    def __init__(self, app, **kwargs):
        self.config = kwargs

    def _register(self, app, *args):
        table = str.maketrans("/", "_", "0123456789{}[]^+-*:.?()$")
        for path in args:
            base = "_".join(
                i.split(":")[0].translate(table)
                for i in urllib.parse.urlparse(path).path.split("/")
                if i
            )
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
            "/fonts/{path:[^{}]+}",
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
    def fonts_path_get(self, request):
        path = request.match_info["path"]
        if ".." in path:
            return aiohttp.web.HTTPForbidden()
        else:
            data = pkg_resources.resource_string(
                "addisonarches.web",
                "static/fonts/{}".format(path)
            )

            return aiohttp.web.Response(
                body=data,
                content_type=(
                    "application/font-ttf" if path.endswith("ttf") else "application/font-woff"
                )
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

class Registration(Service):

    sessions = {}

    def __init__(self, app, token, down, up, **kwargs):
        super().__init__(app, **kwargs)
        self.token = token
        self.down = down
        self.up = up
        self.routes = dict(list(self._register(
            app,
            "/start",
        )))

    def start(self, items=[]):
        session = uuid.uuid4().hex
        ts = time.time()
        self.sessions[session] = ts
        return {
            "info": {
                "args": self.config.get("args"),
                "interval": 200,
                "session": session,
                "time": "{:.1f}".format(ts),
                "title": "Addison Arches {}".format(__version__),
                "version": __version__
            },
            "items": OrderedDict([(str(id(i)), i) for i in items]),
        }

    @asyncio.coroutine
    def start_get(self, request):
        tmplt = pyratemp.Template(filename="start.prt", loader_class=TemplateLoader)
        return aiohttp.web.Response(
            content_type="text/html",
            text=tmplt(**self.start())
        )

    @asyncio.coroutine
    def start_post(self, request):
        data = yield from request.post()
        log = logging.getLogger("addisonarches.web.services.start_post")
        session = data.getone("session")
        try:
            ts, Registration.sessions[session] = Registration.sessions[session], time.time()
        except KeyError:
            log.warning("Session not found: {}".format(session))
            return aiohttp.web.HTTPFound("/titles")
        else:
            log.info(
                "Initiating game for session {0} ({1}s)".format(
                    session,
                    Registration.sessions[session] - ts
                )
            )

        # TODO: hateoas
        # form = RegistrationView(data)
        # if form.invalid:
        # raise HTTPBadRequest(
        #     "Bad value in '{}' field".format(form.invalid[0].name))

        # TODO: turberfield.dialogue.types.Name
        name = data.getone("name")
        root = self.config["output"]
        if session not in Workflow.sessions:
            progress = Persistent.make_path(Persistent.recent_slot(
                Persistent.Path(root, session, None, "progress.rson")
            ))
            args = [
                sys.executable,
                "-m", "addisonarches.main",
                "--output", root,
                "--session", session,
                "--name", name,
                "--log", os.path.join(root, session, progress.slot, "run.log")
            ]
            log.info("Job: {0}".format(args))
            try:
                worker = subprocess.Popen(
                    args,
                    # cwd=app.config.get("args")["output"],
                    shell=False
                )
            except OSError as e:
                log.error(e)
            else:
                log.info("Launched worker {0.pid}".format(worker))
            Workflow.sessions[session] = (progress, self.down, self.up)
        return aiohttp.web.HTTPFound("/{}".format(session))

class Workflow(Service):

    sessions = {}

    def __init__(self, app, token, down, up, **kwargs):
        super().__init__(app, **kwargs)
        self.token = token
        self.down = down
        self.up = up
        self.routes = dict(list(self._register(
            app,
            "/{session:[a-z0-9]{32}}",
            "/{session:[a-z0-9]{32}}/asks",
            "/{session:[a-z0-9]{32}}/bids",
            "/{session:[a-z0-9]{32}}/buying",
            "/{session:[a-z0-9]{32}}/inventory",
            "/{session:[a-z0-9]{32}}/splits",
            "/{session:[a-z0-9]{32}}/selling",
            "/{session:[a-z0-9]{32}}/vias",
        )))

    def inventory(self, session, items=[]):
        ts = time.time()
        path, down, up = self.sessions[session]
        items = items or get_objects(path._replace(file="inventory.rson"))
        groups = group_by_type(items)
        totals = Counter(groups[Game.Item])

        location = next(iter(groups[Location]), None)
        items = [item(i, session=session, totals=totals)
                 for i in groups[Game.Item]]

        for view in items:
            del view.actions["buy"]
            if location is None or location.name != "Addison Arches 18a":
                view.actions.pop("split", None)

        return {
            "info": {
                "args": self.config.get("args"),
                "interval": 200,
                "session": session,
                "time": "{:.1f}".format(ts),
                "title": "Addison Arches {}".format(__version__),
                "version": __version__,
            },
            "nav": [],
            "items": items,
        }

    def frame(self, session, items=[]):
        rv = self.progress(session, items)
        path, down, up = self.sessions[session]
        items = items or get_objects(path._replace(file="frame.rson"))
        if items:
            rv["info"]["interval"] = 1.5 + 0.2 * items[-1].text.count(" ")
            rv["items"].extend([dialogue(i, session=session) for i in items])
        avatars = get_objects(path._replace(file="diorama.rson"))
        rv["diorama"] = avatars
        return rv

    def progress(self, session, items=[]):
        """
        Metadata about the game session.

        """
        ts = time.time()
        path, down, up = self.sessions[session]
        items = items or get_objects(path)
        groups = group_by_type(items)
        totals = Counter(groups[Game.Item])

        items = OrderedDict(
            [(i, item(i, session=session, totals=totals))
             for i in groups[Game.Item]]
        )
        location = next(iter(groups[Location]), None)

        # TODO: Needs to go in business layer
        pending = getattr(next(iter(groups[Game.Drama]), None), "type", None)

        for view in items.values():
            del view.actions["sell"]
            if location.name == "Addison Arches 18a":
                del view.actions["buy"]
            elif pending == "Buying":
                del view.actions["buy"]
                view.actions.pop("split", None)
            else:
                view.actions.pop("split", None)

        return {
            "info": {
                "args": self.config.get("args"),
                "interval": 2 if location is None else 12,
                "session": session,
                "time": "{:.1f}".format(ts),
                "title": "Addison Arches {}".format(__version__),
                "version": __version__,
                "location": location,
            },
            "nav": [via(i, session=session) for i in groups[Game.Via]],
            "items": (
                [tick(i, session=session) for i in groups[Clock.Tick]] +
                [character(i, session=session) for i in groups[Character]] +
                [tally(i, session=session) for i in groups[Game.Tally]] +
                [patter(i, session=session) for i in groups[Trader.Patter]] +
                [drama(i, session=session) for i in groups[Game.Drama]] + list(items.values()) +
                [alert(i, session=session) for i in groups[Alert]]
            )
        }

    @asyncio.coroutine
    def session_inventory_get(self, request):
        session = request.match_info["session"]
        tmplt = pyratemp.Template(
            filename="inventory.html.prt",
            loader_class=TemplateLoader
        )

        return aiohttp.web.Response(
            content_type="text/html",
            text=tmplt(**self.inventory(session))
        )

    @asyncio.coroutine
    def session_get(self, request):
        session = request.match_info["session"]
        path, down, up = self.sessions[session]

        tmplt = pyratemp.Template(
            filename="session.html.prt",
            loader_class=TemplateLoader
        )
        text = tmplt(**self.frame(session))

        msg = parcel(
            self.token, None,
            dst=Address(
                self.token.namespace, self.token.user, self.token.service, session
            )
        )
        yield from down.put(msg)
        return aiohttp.web.Response(
            content_type="text/html",
            text=text
        )

    @asyncio.coroutine
    def session_asks_post(self, request):
        log = logging.getLogger("addisonarches.web.session_asks_post")
        session = request.match_info["session"]
        data = yield from request.post()
        log.debug(data.items())
        view = ask(data, session=session)
        problems = view.rejects("ask")
        for prob in problems:
            log.warning(prob)

        if not problems:
            log.debug(view.obj)
            path, down, up = self.sessions[session]
            msg = parcel(
                self.token, view.obj,
                dst=Address(
                    self.token.namespace, self.token.user, self.token.service, session
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()
            log.debug(reply)
        return aiohttp.web.HTTPFound("/{}".format(session))

    @asyncio.coroutine
    def session_bids_post(self, request):
        log = logging.getLogger("addisonarches.web.session_bids_post")
        session = request.match_info["session"]
        data = yield from request.post()
        log.debug(data.items())
        view = bid(data, session=session)
        problems = view.rejects("bid")
        for prob in problems:
            log.warning(prob)

        if not problems:
            log.debug(view.obj)
            path, down, up = self.sessions[session]
            msg = parcel(
                self.token, view.obj,
                dst=Address(
                    self.token.namespace, self.token.user, self.token.service, session
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()
            log.debug(reply)
        return aiohttp.web.HTTPFound("/{}".format(session))

    @asyncio.coroutine
    def session_buying_post(self, request):
        log = logging.getLogger("addisonarches.web.session_buying_post")
        session = request.match_info["session"]
        data = yield from request.post()
        view = item(data, session=session)
        problems = view.rejects("buy")
        for prob in problems[:]:
            if prob.name == "description":
                problems.remove(prob)

        if not problems:
            log.debug(view.obj)
            path, down, up = self.sessions[session]
            drama = Buying(memory=[view.obj])
            msg = parcel(
                self.token, drama,
                dst=Address(
                    self.token.namespace, self.token.user, self.token.service, session
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()
            log.debug(reply)
        return aiohttp.web.HTTPFound("/{}".format(session))

    @asyncio.coroutine
    def session_selling_post(self, request):
        log = logging.getLogger("addisonarches.web.session_selling_post")
        session = request.match_info["session"]
        data = yield from request.post()
        view = item(data, session=session)
        problems = view.rejects("sell")
        for prob in problems[:]:
            log.warning(prob)
            if prob.name == "description":
                problems.remove(prob)

        if not problems:
            log.debug(view.obj)
            path, down, up = self.sessions[session]
            drama = Selling(memory=[view.obj])
            msg = parcel(
                self.token, drama,
                dst=Address(
                    self.token.namespace, self.token.user, self.token.service, session
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()
            log.debug(reply)
        return aiohttp.web.HTTPFound("/{}".format(session))

    @asyncio.coroutine
    def session_splits_post(self, request):
        log = logging.getLogger("addisonarches.web.session_splits_post")
        session = request.match_info["session"]
        data = yield from request.post()
        log.debug(data.items())
        view = item(data, session=session)
        problems = view.rejects("split")
        for prob in problems[:]:
            log.warning(prob)
            if prob.name == "description":
                problems.remove(prob)

        if not problems:
            log.debug(view.obj)
            path, down, up = self.sessions[session]
            msg = parcel(
                self.token, view.obj,
                dst=Address(
                    self.token.namespace, self.token.user, self.token.service, session
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()
            log.debug(reply)
        return aiohttp.web.HTTPFound("/{}".format(session))

    @asyncio.coroutine
    def session_vias_post(self, request):
        log = logging.getLogger("addisonarches.web.session_vias_post")
        session = request.match_info["session"]
        data = yield from request.post()
        log.debug(data.items())
        view = via(data, session=session)
        problems = view.rejects("go")
        for prob in problems:
            log.warning(prob)

        if not problems:
            log.debug(view.obj)
            dst = Address(
                self.token.namespace, self.token.user, self.token.service, session
            )
            log.debug(dst)
            path, down, up = self.sessions[session]
            msg = parcel(
                self.token, view.obj,
                dst=Address(
                    self.token.namespace, self.token.user, self.token.service, session
                )
            )
            yield from down.put(msg)
            reply = yield from up.get()
            log.debug(reply)
        return aiohttp.web.HTTPFound("/{}".format(session))

class Transitions(Service):

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.routes = dict(list(self._register(
            app,
            "/",
            "/titles"
        )))

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
    def _get(self, request):
        return aiohttp.web.HTTPFound("/titles")

    @asyncio.coroutine
    def titles_get(self, request):
        tmplt = pyratemp.Template(
            filename="titles.prt", loader_class=TemplateLoader
        )
        return aiohttp.web.Response(
            content_type="text/html",
            text=tmplt(**self.titles())
        )
