from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.services.i18n import Translator, resolve_locale


def i18n_context(request: Request) -> dict:
    """Inject the request's locale and translation helpers into every template."""

    locale = resolve_locale(request.headers.get("accept-language"))
    translator = Translator(locale)

    return {
        "lang": locale,
        "t": translator,
        "plural": translator.plural,
        # Strings needed by client-side JS, serialized into ``window.I18N``.
        "js_i18n": translator.data.get("js", {}),
    }


templates = Jinja2Templates(
    directory="app/templates",
    context_processors=[i18n_context],
)
