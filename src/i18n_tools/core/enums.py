from enum import Enum

from i18n_tools.core.errors import InvalidLocaleStyle


class LocaleStyle(Enum):
    PER_NAMESPACE = "per-namespace"
    PER_LOCALE = "per-locale"
    UNKNOWN = "unknown"

    @classmethod
    def of(cls, style_str: str) -> "LocaleStyle":
        for style in cls:
            if style.value == style_str:
                return style
        raise InvalidLocaleStyle(style_str)
