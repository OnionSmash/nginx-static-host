# NGINX Static Host + AI Backend (demo.stacklume.cloud)

A Docker-based setup for hosting a fast, secure static website with NGINX **and** a fully functional AI backend featuring RAG (Retrieval-Augmented Generation) and document ingestion. All containers are based on Alpine Linux for a minimal footprint.

## Architecture

```
Browser
  │
  ▼
nginx:alpine  (port 8080)
  ├── /            → serves static files from public/
  └── /api/*       → proxies to FastAPI backend
                          │
                          ▼
                   python:3.12-alpine  (port 8000)
                   FastAPI + LangChain + ChromaDB client
                          │
                          ▼
                   chromadb/chroma  (port 8001)
                   Vector store (persistent volume)
```

## Versions

This repository offers two versions of the static hosting layer, each catering to different needs:

*   **Version 1.0**: Basic NGINX setup for serving a static website.
*   **Version 1.1**: Enhanced version with security headers, Gzip compression, asset caching, and an `/api/` reverse-proxy to the AI backend.

The `Dockerfile` and `nginx.conf` for each version are in `docker/nginx/<version>/`.

## Features

*   **Lightweight**: Based on `nginx:alpine` and `python:3.12-alpine` — minimal image sizes.
*   **Secure**: Security headers, non-root container user, HTTPS-ready.
*   **Performant**: Gzip, long-lived asset caching, streaming proxy.
*   **RAG-ready**: Ask questions over your own documents via `/api/chat`.
*   **Multi-source ingestion**: Ingest PDFs, plain text, or web URLs via `/api/ingest/*`.
*   **Local-first**: One `docker compose up --build` starts everything.

## Quick Start (Local)

> **Prerequisite:** Docker and Docker Compose installed.

```bash
# 1. Clone and enter the repo
git clone https://github.com/OnionSmash/nginx-static-host.git
cd nginx-static-host

# 2. Configure your OpenAI API key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 3. Start the full stack
docker compose up --build
```

| Service  | URL                              | Purpose                       |
|----------|----------------------------------|-------------------------------|
| Frontend | http://localhost:8080            | Static site + AI chat UI      |
| Backend  | http://localhost:8000/api/docs   | FastAPI docs (Swagger UI)     |
| ChromaDB | http://localhost:8001            | Vector store (internal use)   |

### Ingest documents

```bash
# Ingest a PDF
curl -X POST http://localhost:8000/api/ingest/pdf \
  -F "file=@/path/to/document.pdf"

# Ingest a URL
curl -X POST http://localhost:8000/api/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/docs"}'

# Ingest plain text
curl -X POST http://localhost:8000/api/ingest/text \
  -H "Content-Type: application/json" \
  -d '{"content": "Your text here", "source_name": "my-doc"}'
```

### Query the RAG endpoint

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Stacklume?"}'
```

---

## Static-Only Setup Instructions

These instructions will guide you through setting up a static site on a host or server.

### 1. Create a Project Folder

First, create a directory for your project and navigate into it.

```bash
mkdir ~/my-static-site && cd ~/my-static-site
```

All subsequent commands should be run from within this directory.

### 2. Add Your Static Files

Place your website's files, such as HTML, CSS, JavaScript, and images, into a sub-folder named `public`.

```bash
mkdir public
echo '<h1>Hello, Docker + NGINX!</h1>' > public/index.html
# (Copy the rest of your site into ./public)
```

NGINX will serve the contents of the `public` directory.

### 3. Add a Custom NGINX Configuration

For most simple websites, the default configuration provided by NGINX is sufficient. However, for more advanced features like clean URLs, enhanced caching, or specific configurations for Single-Page Applications (SPAs), a custom `nginx.conf` is necessary.

You can find the `nginx.conf` files for each version in the `docker/nginx` directory of this repository.

*   **For Version 1.0 (Basic):** This configuration sets up a basic server to listen on port 80 and serve files.
*   **For Version 1.1 (Secure & Performant):** This version includes optimisations such as security headers, caching policies for different file types, and Gzip compression to improve performance.

Choose the configuration that best suits your needs and place it in the root of your project folder. NGINX configuration is controlled by directives organised into blocks or contexts. For example, the `server` block defines the settings for a virtual server, and the `location` block is used to configure how NGINX handles requests for different URIs.

### 4. Create a Dockerfile

The `Dockerfile` is a text file that contains the commands to assemble a Docker image. You will find a `Dockerfile` for each version inside the `docker/nginx` directory.

The `Dockerfile` performs the following steps:
*   **`FROM nginx:alpine`**: Specifies the lightweight `nginx:alpine` image as the base for our build.
*   **`COPY public/ /usr/share/nginx/html`**: Copies your static files from the `public` directory on your host into the webroot of the NGINX server inside the container.
*   **`COPY nginx.conf /etc/nginx/conf.d/default.conf`**: Copies your custom `nginx.conf` into the NGINX configuration directory within the container, overwriting the default configuration.
*   **`EXPOSE 80`**: Informs Docker that the container listens on port 80 at runtime.

Copy the appropriate `Dockerfile` from the repository into the root of your project directory.

### 5. Build the Image

Now, build the Docker image from your `Dockerfile`.

```bash
docker build -t my-static-site:1.0 .
```

The `-t` flag tags the image with a name and version. The `.` at the end specifies that the build context is the current directory.

### 6. Run the Container Locally

Finally, run the container from the image you just built.

```bash
docker run -d --name my-static-site \
  -p 8080:80 \
  my-static-site:1.0
```

*   `-d`: Runs the container in detached mode (in the background).
*   `-p 8080:80`: Maps port 8080 on the host to port 80 inside the container.

You can now visit `http://localhost:8080` in your web browser to see your site.

**Development Workflow:** When you make changes to your site's files in the `public` directory, you will need to rebuild the image and restart the container. For a more rapid development cycle, consider using a bind mount:

```bash
docker run -d -p 8080:80 -v $(pwd)/public:/usr/share/nginx/html nginx:alpine
```

This command mounts the `public` directory on your host directly into the container, so changes are reflected immediately without needing to rebuild the image.
