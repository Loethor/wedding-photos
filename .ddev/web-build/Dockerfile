ARG BASE_IMAGE
FROM $BASE_IMAGE

# Install uv (Python package manager) system-wide so it's on PATH for all users.
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin UV_UNMANAGED_INSTALL=1 sh

# Storage directory the app writes uploads/thumbnails to (see app/config.py PHOTO_STORAGE).
RUN mkdir -p /srv/photo-data/wedding-photos && chmod -R 777 /srv/photo-data
