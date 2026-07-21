"""Internationalization: language files + locale resolution.

Texts live in ``app/locales/<locale>.json`` as nested dicts. Keys are addressed
with dots (``"gallery.empty"``). Values may contain ``{placeholders}`` filled via
``str.format``; plural entries are ``{"one": ..., "other": ...}`` objects resolved
by :meth:`Translator.plural`.

The locale is picked from the browser's ``Accept-Language`` header: Spanish when
the most-preferred language is Spanish, English otherwise.
"""

import json
from pathlib import Path
from typing import Any

LOCALES_DIR = Path(__file__).parent.parent / "locales"

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("es", "en")


def _load(locale: str) -> dict[str, Any]:
    with open(LOCALES_DIR / f"{locale}.json", encoding="utf-8") as fh:
        return json.load(fh)


TRANSLATIONS: dict[str, dict[str, Any]] = {loc: _load(loc) for loc in SUPPORTED_LOCALES}


def resolve_locale(accept_language: str | None) -> str:
    """Return the best supported locale for an ``Accept-Language`` header.

    Spanish if the highest-priority language the browser asks for is Spanish;
    English in every other case (including when the header is missing).
    """

    if not accept_language:
        return DEFAULT_LOCALE

    best_lang: str | None = None
    best_q = -1.0

    for part in accept_language.split(","):
        segments = part.split(";")
        tag = segments[0].strip().lower()
        if not tag or tag == "*":
            continue

        quality = 1.0
        for segment in segments[1:]:
            segment = segment.strip()
            if segment.startswith("q="):
                try:
                    quality = float(segment[2:])
                except ValueError:
                    quality = 0.0

        if quality > best_q:
            best_q = quality
            best_lang = tag

    if best_lang and (best_lang == "es" or best_lang.startswith("es-")):
        return "es"

    return DEFAULT_LOCALE


def _lookup(data: dict[str, Any], key: str) -> Any:
    node: Any = data
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


class Translator:
    """Locale-bound lookup helper exposed to templates as ``t`` / ``plural``."""

    def __init__(self, locale: str) -> None:
        self.locale = locale
        self.data = TRANSLATIONS.get(locale, TRANSLATIONS[DEFAULT_LOCALE])

    def _resolve(self, key: str) -> Any:
        value = _lookup(self.data, key)
        if value is None:
            value = _lookup(TRANSLATIONS[DEFAULT_LOCALE], key)
        return value

    def __call__(self, key: str, **kwargs: Any) -> str:
        value = self._resolve(key)
        if value is None:
            # Unknown key (e.g. a framework-supplied error detail): show it raw.
            return key
        if isinstance(value, str):
            return value.format(**kwargs) if kwargs else value
        return key

    def plural(self, key: str, n: int, **kwargs: Any) -> str:
        value = self._resolve(key)
        if not isinstance(value, dict):
            return key
        form = value.get("one" if n == 1 else "other", "")
        return form.format(n=n, **kwargs)
