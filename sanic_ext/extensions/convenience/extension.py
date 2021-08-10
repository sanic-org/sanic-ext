from ..base import Extension


class SerializerExtension(Extension):
    name = "serializer"

    def startup(self, _) -> None:
        ...
