from ..base import Extension
from .setup import setup_livereload


class LivereloadExtension(Extension):
    name = "livereload"
    MIN_VERSION = (23, 6)

    def startup(self, bootstrap) -> None:
        if self.included():
            setup_livereload(self.app)

    def included(self):
        return self.config.LIVERELOAD
