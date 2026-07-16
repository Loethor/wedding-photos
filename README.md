# Wedding Photos

Simple web application to upload and browse wedding photos and videos.

## Features

- Upload photos and videos
- Organize uploads by first and last name
- Browse all photos
- Browse photos by person
- Automatic thumbnail generation
- Mobile-friendly interface
- Password protected access

---

## Requirements

- Python 3.12+
- uv
- nginx (production deployment)

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

```
http://127.0.0.1:8000
```

---

## Production

The application uses **nginx as a reverse proxy** in front of FastAPI.

Architecture:

```
Client
  |
  | HTTP :80
  v
nginx
  |
  | localhost:8000
  v
FastAPI (uvicorn)
```

FastAPI should only listen locally:

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

nginx provides:

- External HTTP access
- Reverse proxy to FastAPI
- Large file upload handling
- Future HTTPS support

---

## nginx setup

Install nginx:

```bash
sudo apt update
sudo apt install nginx
```

Create a site configuration:

```bash
sudo nano /etc/nginx/sites-available/wedding-photos
```

Example configuration:

```nginx
server {

    listen 80;

    server_name _;

    client_max_body_size 1G;

    location / {

        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_read_timeout 600;
        proxy_send_timeout 600;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/wedding-photos \
/etc/nginx/sites-enabled/
```

Disable the default nginx page:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Test configuration:

```bash
sudo nginx -t
```

Reload nginx:

```bash
sudo systemctl reload nginx
```

The application will then be available at:

```
http://<server-ip>
```

---

## Firewall

Only nginx should be exposed externally.

Allow HTTP:

```bash
sudo ufw allow 80/tcp
```

Remove direct FastAPI access:

```bash
sudo ufw delete allow 8000/tcp
```

FastAPI remains accessible only locally through nginx.

---

## Storage

Configure the storage folder in:

```
app/config.py
```

Example:

```python
PHOTO_STORAGE = Path("/srv/photo-data")
```

---

## Project structure

```
app/
storage/
pyproject.toml
```

---

## Supported files

### Images

- jpg
- jpeg
- png
- webp
- heic
- heif

### Videos

- mp4
- mov
- m4v

---

## Generate thumbnails

Thumbnails are generated automatically during upload.

Images use Pillow.

Videos use ffmpeg to extract a preview frame.

---

## Environment variables

Required:

```bash
WEDDING_PASSWORD
SECRET_KEY
```

Example:

```bash
export WEDDING_PASSWORD="your-password"
export SECRET_KEY="your-secret-key"
```

---

## Running the application

Start FastAPI:

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then access through nginx:

```
http://<server-ip>
```