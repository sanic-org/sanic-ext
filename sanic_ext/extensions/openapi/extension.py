from ..base import Extension
from .blueprint import blueprint_factory


class OpenAPIExtension(Extension):
    name = "openapi"

    def startup(self, _) -> None:
        if self.app.config.OAS:
            self.bp = blueprint_factory(self.app.config)
            self.app.blueprint(self.bp)

    def label(self):
        if self.app.config.OAS:
            name = f"{self.bp.name}.index"

            if "SERVER_NAME" in self.app.config:
                return f"[{self.app.url_for(name, _external=True)}]"

        return ""
