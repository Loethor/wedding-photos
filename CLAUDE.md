# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

FastAPI web app for guests to upload and browse wedding photos/videos. Single shared
password protects the whole site; there are no user accounts. Files live on disk (not a
database), organized into one folder per uploader.

## Commands

```bash
uv sync                                                    # install deps (incl. dev)
uv run uvicorn app.main:app --reload                       # run locally (dev)
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000   # run (prod, behind nginx)
uv run ruff check .                                         # lint
uv run ruff format .                                        # format
uv run mypy app                                             # type check
```

There is no test suite.

Two environment variables are **required** at startup (the app raises `KeyError` on import
without them, see `app/config.py`):

```bash
export WEDDING_PASSWORD="..."
export SECRET_KEY="..."   # used to sign session cookies
```

Video thumbnails shell out to `ffmpeg`, which must be on `PATH`.

## Architecture

Request flow: **nginx → uvicorn/FastAPI**. nginx is the reverse proxy handling external
access and large uploads; FastAPI listens only on localhost in production.

- `app/main.py` — assembles the app: mounts routers, adds middleware, registers the global
  `HTTPException` handler that renders `error.html`. Middleware order matters:
  `SessionMiddleware` is added after `AuthenticationMiddleware`, so at request time sessions
  are resolved first (outermost) and auth runs with `request.session` available.
- `app/middleware/authentication.py` — global gate. Every path except `/login` and
  `/favicon.ico` requires `request.session["authenticated"]`; otherwise redirects to
  `/login`. New public endpoints must be added to `public_paths` here.
- `app/routes/` — `auth` (login + rate limiting), `upload`, `gallery` (HTML pages),
  `files` (serves photo/video/thumbnail/download).
- `app/services/` — `storage` (folder/file layout + sanitization), `thumbnails`
  (Pillow for images, ffmpeg for videos), `security` (path-traversal guard), `rate_limit`.
- `app/web.py` — shared `Jinja2Templates` instance; import `templates` from here, don't
  re-create it.
- `app/templates/` — server-rendered Jinja2. `base.html` is the layout; pages extend it.

### Storage layout (the source of truth — there is no DB)

`PHOTO_STORAGE` (hardcoded to `/srv/photo-data/wedding-photos` in `app/config.py`; a
commented `./storage` line is the local-dev alternative) contains:

```
<PHOTO_STORAGE>/
  First_Last/            # one folder per uploader ("person"), name = first_last
    photo.jpg
  .thumbnails/
    First_Last/
      photo.jpg          # thumbnails are ALWAYS .jpg, keyed by original stem
```

Listing "people" = listing top-level dirs (dotfiles like `.thumbnails` are skipped).
The `person` in URLs like `/photo/{person}/{filename}` is the sanitized folder name.

### Conventions that span files

- **Filename/folder sanitization** lives in `app/services/storage.py`
  (`sanitize_folder_name`, `sanitize_filename`): strip accents → ASCII, replace non-
  alphanumerics with `_`. Uploader name comes in as `first_name` + `last_name` form fields,
  joined as `first_last`. Any code that maps a name to a path must go through these.
- **Allowed file types** are the `IMAGE_EXTENSIONS` / `VIDEO_EXTENSIONS` / `ALLOWED_EXTENSIONS`
  sets in `storage.py` — the single place to change what's accepted. Enforced on save.
- **Path-traversal defense**: any endpoint serving a file by user-supplied path must call
  `safe_path()` (`app/services/security.py`), which resolves the path and confirms it stays
  under `PHOTO_STORAGE`. `files.py:validate_file` is the pattern to follow.
- **Uploads** stream to disk in 1 MB chunks and abort past `MAX_UPLOAD_SIZE` (1 GB),
  deleting the partial file. Name collisions get a `_1`, `_2`, … suffix.
- **Rate limiting** is in-memory per-process (`RateLimiter`, a dict of timestamps) — it does
  not survive restarts and is not shared across workers. Login is limited to 5 attempts/60s
  per client IP.
