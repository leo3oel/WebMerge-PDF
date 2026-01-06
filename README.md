# PDF Combiner & Editor (Flask)

A self-hosted Flask web application for merging, reordering, rotating, and renaming PDF files.  
It is designed to sit between a document scanner and Paperless-ngx in NAS-based workflows.

---

## Overview

The app processes PDF files from an input directory, allows manual editing via a web interface, and saves the final document with a configurable filename prefix.

Main workflow:
1. Select input PDFs
2. Reorder and rotate pages
3. Preview the result
4. Save the merged PDF with a chosen prefix

The prefix list is configurable and can be modified without rebuilding the container.

---

## Use Case

My scanner uploads PDFs to an SMB share which is normally imported directly by Paperless.  
For large or multi-part documents, this app provides an intermediate step:

1. Scan PDFs to an SMB share mounted as the app’s input folder
2. Edit and merge PDFs via the web UI
3. Save the final PDF into Paperless import folder
4. Paperless imports the cleaned document

Filename prefixes are used to support different Paperless users or import rules.

---

## Features

- PDF selection from an input folder
- Page reordering and rotation
- PDF merging
- Preview before saving
- Configurable filename prefixes
- Docker-based deployment

---

## Docker Usage

**Docker Image:**  
https://hub.docker.com/r/leo3oel/webmergepdf

The app is designed to run in a container and relies on mounted volumes.

Required container paths:
- `/app/static/input` – input PDFs
- `/app/output` – processed PDFs
- `/app/static/data` – persistent data (e.g. SQLite)

Example Docker Compose:

```yaml
services:
  webmergepdf:
    image: leo3oel/webmergepdf:latest
    environment:
      SECRET_KEY: secret-key
    ports:
     - "8000:8000"
    restart: unless-stopped
    volumes:
      - bind:
          create_host_path: False
          propagation: rprivate
        read_only: False
        source: /webmergepdf-data
        target: /app/static/data
        type: bind
      - bind:
          create_host_path: False
          propagation: rprivate
        read_only: False
        source: /Paperless/Import
        target: /app/output
        type: bind
      - bind:
          create_host_path: False
          propagation: rprivate
        read_only: False
        source: /webmergepdf-input
        target: /app/static/input
        type: bind
```