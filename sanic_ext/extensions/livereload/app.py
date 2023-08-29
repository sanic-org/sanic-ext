from asyncio import sleep
from multiprocessing import Queue
from pathlib import Path
from queue import Empty
from typing import Any

import ujson
from sanic import Request, Sanic, Websocket


class Livereload:
    SERVER_NAME = "Reloader"
    HELLO = {
        "command": "hello",
        "protocols": [
            "http://livereload.com/protocols/official-7",
        ],
        "serverName": SERVER_NAME,
    }

    def __init__(
        self, reload_queue: Queue, debug: bool, state: dict[str, Any]
    ):
        self.reload_queue = reload_queue
        self.app = Sanic(self.SERVER_NAME)
        self.debug = debug
        self.state = state
        self.app.static(
            "/livereload.js", Path(__file__).parent / "livereload.js"
        )
        self.app.add_websocket_route(
            self.livereload_handler, "/livereload", name="livereload"
        )
        self.app.add_task(self._listen_to_queue())
        self.app.config.EVENT_AUTOREGISTER = True

    def run(self):
        kwargs = {
            "debug": self.debug,
            "access_log": False,
            "single_process": True,
            "port": 35729,
        }
        self.app.run(**kwargs)

    async def _listen_to_queue(self):
        while True:
            try:
                self.reload_queue.get_nowait()
            except Empty:
                await sleep(0.5)
                continue
            await self.app.dispatch("livereload.file.reload")

    async def livereload_handler(self, request: Request, ws: Websocket):
        await ws.recv()
        await ws.send(ujson.dumps(self.HELLO))

        while True:
            await request.app.event("livereload.file.reload")
            await self._wait_for_state()
            await ws.send(ujson.dumps({"command": "reload", "path": "..."}))

    async def _wait_for_state(self):
        while True:
            states = [
                state.get("ready")
                for state in self.state.values()
                if state.get("server")
            ]
            if all(states):
                await sleep(0.5)
                break
