# NGINX Static Host

A simple Docker setup using NGINX to host fast, secure static websites. This repository provides a straightforward and efficient way to serve static content.

## Versions

This repository offers two versions, each catering to different needs:

*   **Version 1.0**: The initial, basic setup for serving a static website with NGINX.
*   **Version 1.1**: An enhanced version with added security and performance features.

The `Dockerfile` and `nginx.conf` for each version are located within their respective version directories in the repository.

## Features

*   **Lightweight**: Based on the official NGINX Alpine image, keeping the footprint small.
*   **Secure**: Provides a solid foundation for a secure static site. Version 1.1 includes additional security headers.
*   **Performant**: Configured for efficient delivery of static assets with caching headers.
*   **Simple**: Easy to understand and set up, even for those new to Docker or NGINX.

## HTML Files

This repository contains the following HTML file:

| File | Description |
|------|-------------|
| `public/index.html` | The main (and only) page of the static site. It contains the full single-page layout with a hero section, an about section with feature cards, and a contact section. |

All HTML content lives inside the `public/` directory, which is the webroot that NGINX serves.

## Theme

The site uses a **custom hand-written CSS theme** located at `public/css/styles.css`. There is no external CSS framework (e.g. Bootstrap or Tailwind). Key design decisions:

| Element | Value |
|---------|-------|
| **Primary color** | Indigo `#4f46e5` |
| **Accent / gradient end** | Violet `#7c3aed` |
| **Hero background** | Linear gradient `135deg`, indigo → violet |
| **Body background** | White `#ffffff` |
| **Section background** | Light gray `#f9fafb` |
| **Footer background** | Dark indigo `#1e1b4b` |
| **Font stack** | System UI (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, Roboto, Helvetica, Arial) |
| **Layout** | CSS Grid for the feature cards; Flexbox for navigation and hero |

The color palette mirrors the Tailwind CSS `indigo-600` / `violet-600` hues, but the CSS is entirely custom with no dependency on Tailwind.

## Setup Instructions

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

---

## Running Locally on macOS

### Prerequisites

Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) (supports both Intel and Apple Silicon). Once installed, start Docker Desktop and wait until the whale icon in the menu bar shows **"Docker Desktop is running"**.

### Quick Start (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/OnionSmash/nginx-static-host.git
cd nginx-static-host

# 2. Build the image using the Version 1.1 Dockerfile
docker build \
  -f docker/nginx/1.1/dockerfile \
  -t nginx-static-host:local .

# 3. Run the container
docker run -d --name nginx-static-host \
  -p 8080:80 \
  nginx-static-host:local
```

Open your browser at **http://localhost:8080**.

### Live-reload during development

For a faster feedback loop while editing files in `public/`, use a bind mount instead of rebuilding the image every time:

```bash
docker run -d --name nginx-static-dev \
  -p 8080:80 \
  -v "$(pwd)/public:/usr/share/nginx/html:ro" \
  nginx:alpine
```

Edit any file in `public/` and simply refresh the browser — no rebuild needed.

### Stopping and cleaning up

```bash
docker stop nginx-static-host
docker rm   nginx-static-host
```

---

## Deploying on a Linode Ubuntu Docker Server

These steps assume you have a Linode VPS running Ubuntu (20.04 or 22.04) and a user with `sudo` privileges.

### 1. Install Docker on the Linode

SSH into the server and run:

```bash
# Update package index and install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key and repository
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Allow your user to run Docker without sudo (re-login after this)
sudo usermod -aG docker $USER
```

Log out and back in so the group change takes effect, then verify:

```bash
docker --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/OnionSmash/nginx-static-host.git
cd nginx-static-host
```

### 3. Build the Production Image

```bash
docker build \
  -f docker/nginx/1.1/dockerfile \
  -t nginx-static-host:latest .
```

### 4. Run the Container

```bash
docker run -d \
  --name nginx-static-host \
  --restart unless-stopped \
  -p 80:80 \
  nginx-static-host:latest
```

*   `--restart unless-stopped` — the container restarts automatically if the server reboots or Docker restarts.
*   `-p 80:80` — maps the host's port 80 directly so the site is reachable without a port number.

Verify the site is up:

```bash
curl -I http://localhost
```

### 5. (Optional) Enable HTTPS with Let's Encrypt

For a production deployment, run [Certbot](https://certbot.eff.org/) on the host or add an [NGINX proxy with SSL termination](https://nginxproxymanager.com/) in front of this container. Point your domain's DNS A record to your Linode's IP address first.

### 6. Updating the Site

When you push new content, update the server with:

```bash
cd nginx-static-host
git pull

docker build \
  -f docker/nginx/1.1/dockerfile \
  -t nginx-static-host:latest .

docker stop  nginx-static-host
docker rm    nginx-static-host

docker run -d \
  --name nginx-static-host \
  --restart unless-stopped \
  -p 80:80 \
  nginx-static-host:latest
```
