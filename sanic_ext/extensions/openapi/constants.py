from enum import Enum, auto


class BaseEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        parts = name.split("_")
        return parts[0].lower() + "".join(part.title() for part in parts[1:])


class SecuritySchemeType(BaseEnum):
    API_KEY = auto()
    HTTP = auto()
    OAUTH2 = auto()
    OPEN_ID_CONNECT = auto()


class SecuritySchemeLocation(BaseEnum):
    QUERY = auto()
    HEADER = auto()
    COOKIE = auto()


class SecuritySchemeAuthorization(BaseEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name.title()

    BASIC = auto()
    BEARER = auto()
    DIGEST = auto()
    HOBA = "HOBA"
    MUTUAL = auto()
    NEGOTIATE = auto()
    OAUTH = "OAuth"
    SCRAM_SHA_1 = "SCRAM-SHA-1"
    SCRAM_SHA_256 = "SCRAM-SHA-256"
    VAPID = "vapid"
