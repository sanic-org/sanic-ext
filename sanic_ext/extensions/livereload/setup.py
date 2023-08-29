from multiprocessing import Queue
from typing import Any

from sanic import Sanic

from .app import Livereload


def setup_livereload(app: Sanic) -> None:
    @app.main_process_start
    async def main_process_start(app: Sanic):
        app.shared_ctx.reload_queue = Queue()

    @app.main_process_ready
    async def main_process_ready(app: Sanic):
        app.manager.manage(
            "Livereload",
            _run_reload_server,
            {
                "reload_queue": app.shared_ctx.reload_queue,
                "debug": app.state.is_debug,
                "state": app.manager.worker_state,
            },
        )

    @app.before_server_start
    async def before_server_start(app: Sanic):
        app.shared_ctx.reload_queue.put("reload")

    @app.after_server_start
    async def after_server_start(app: Sanic):
        app.m.state["ready"] = True

    @app.before_server_stop
    async def before_server_stop(app: Sanic):
        try:
            app.m.state["ready"] = False
        except BrokenPipeError:
            ...


def _run_reload_server(
    reload_queue: Queue, debug: bool, state: dict[str, Any]
):
    Livereload(reload_queue, debug, state).run()
