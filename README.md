# Wedding Photos

Simple web application to upload and browse wedding photos and videos.

## Features

- Upload photos and videos
- Organize uploads by first and last name
- Browse all photos
- Browse photos by person
- Automatic thumbnail generation
- Mobile-friendly interface
- No user accounts required

---

## Requirements

- Python 3.12+
- uv

Install uv:

https://docs.astral.sh/uv/

---

## Clone

```bash
git clone https://github.com/<user>/wedding-photos.git
cd wedding-photos
```

---

## Install dependencies

```bash
uv sync
```

---

## Run locally

```bash
uv run uvicorn app.main:app --reload
```

Open:

http://127.0.0.1:8000

---

## Storage

Configure the storage folder in:

app/config.py

Example:

```python
PHOTO_STORAGE = Path("/srv/photo-data")
```

---

## Project structure

app/
storage/
pyproject.toml

---

## Supported files

Images

- jpg
- jpeg
- png
- webp
- heic
- heif

Videos

- mp4
- mov
- m4v

---

## Generate thumbnails

Thumbnails are generated automatically the first time a gallery is opened.

---

## Production

Run:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```