from ..base import Extension
from .blueprint import blueprint_factory


class OpenAPIExtension(Extension):
    name = "openapi"

    def startup(self, _) -> None:
        self.bp = blueprint_factory()
        self.app.blueprint(self.bp)

    def label(self):
        name = f"{self.bp.name}.index"

        if "SERVER_NAME" in self.app.config:
            return f"[{self.app.url_for(name, _external=True)}]"

        return ""
