# NGINX Static Host — Stack Lume Edition

A Docker + NGINX setup for hosting fast, secure static websites. This repository now includes the complete **Stack Lume** Gen AI company website—served across three subdomains with a wildcard Let's Encrypt SSL certificate.

| Domain | Purpose |
|---|---|
| `stacklume.cloud` | Main Gen AI company website |
| `api.stacklume.cloud` | API Developer Hub |
| `demo.stacklume.cloud` | Interactive product demos |

---

## Versions

This repository offers three versions, each catering to different needs:

*   **Version 1.0**: The initial, basic setup for serving a static website with NGINX.
*   **Version 1.1**: An enhanced version with added security headers, Gzip compression, and cache tuning.
*   **Version 1.2**: Multi-domain setup for `stacklume.cloud`, `api.stacklume.cloud`, and `demo.stacklume.cloud` with wildcard Let's Encrypt SSL (DNS-01 challenge via Certbot).

The `Dockerfile` and `nginx.conf` for each version are located within their respective version directories in the repository.

---

## Stack Lume — Quick Deploy

### Prerequisites

*   Docker ≥ 24 and Docker Compose v2
*   A server with ports 80 and 443 open
*   DNS A records pointing to your server IP:
    *   `stacklume.cloud`    → `<server-ip>`
    *   `*.stacklume.cloud`  → `<server-ip>`  *(wildcard A record)*
*   A Cloudflare API token with DNS edit permissions for `stacklume.cloud`

### 1. Clone and Configure

```bash
git clone https://github.com/OnionSmash/nginx-static-host.git
cd nginx-static-host

# Copy the example credentials file and add your Cloudflare API token
cp certbot/cloudflare.ini.example certbot/cloudflare.ini
chmod 600 certbot/cloudflare.ini
# Edit certbot/cloudflare.ini and replace the placeholder token
```

### 2. Obtain the Wildcard SSL Certificate

The wildcard certificate covers **both** `stacklume.cloud` and `*.stacklume.cloud` (which includes `api.stacklume.cloud` and `demo.stacklume.cloud`):

```bash
docker compose run --rm certbot
```

Certbot will use the DNS-01 challenge to verify ownership and write the certificate to the `certbot-certs` Docker volume.

### 3. Start NGINX

```bash
docker compose up -d nginx certbot-renewer
```

The `certbot-renewer` service automatically renews the certificate every 12 hours when it is within 30 days of expiry.

### 4. Verify

```bash
# Check NGINX is running
docker compose ps

# Test HTTPS for all three domains
curl -I https://stacklume.cloud
curl -I https://api.stacklume.cloud
curl -I https://demo.stacklume.cloud
```

### Certificate Renewal

Certbot automatically handles renewal. To force a manual renewal:

```bash
docker compose run --rm certbot-renewer
docker compose exec nginx nginx -s reload
```

---

## Wildcard SSL — How It Works

Let's Encrypt issues wildcard certificates only via the **DNS-01 challenge**, which proves domain ownership by writing a temporary TXT record to your DNS zone. This repository uses the **Certbot Cloudflare DNS plugin** (`certbot/dns-cloudflare`).

If your DNS is managed by a different provider, swap the plugin:

| DNS Provider | Plugin image / package |
|---|---|
| Cloudflare | `certbot/dns-cloudflare` |
| AWS Route 53 | `certbot/dns-route53` |
| Google Cloud DNS | `certbot/dns-google` |
| DigitalOcean | `certbot/dns-digitalocean` |
| Namecheap / other | `certbot/certbot` + manual DNS |

Update the `certbot` and `certbot-renewer` service images in `docker-compose.yml` and the `--dns-*` flags accordingly.

---

## Using a Different DNS Provider (Route 53 Example)

```yaml
# docker-compose.yml — certbot service override for AWS Route 53
certbot:
  image: certbot/dns-route53:latest
  command: >
    certonly
    --dns-route53
    --email hello@stacklume.cloud
    --agree-tos
    --no-eff-email
    -d stacklume.cloud
    -d "*.stacklume.cloud"
  environment:
    - AWS_ACCESS_KEY_ID=YOUR_KEY
    - AWS_SECRET_ACCESS_KEY=YOUR_SECRET
```

---


## Features

*   **Lightweight**: Based on the official NGINX Alpine image, keeping the footprint small.
*   **Secure**: Provides a solid foundation for a secure static site. Version 1.1 includes additional security headers.
*   **Performant**: Configured for efficient delivery of static assets with caching headers.
*   **Simple**: Easy to understand and set up, even for those new to Docker or NGINX.

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
