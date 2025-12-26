# Cloudflare Pages Deployment

## Overview

The braidMgr documentation site is deployed to Cloudflare Pages for fast, global access.

## Setup Instructions

### 1. Create Cloudflare Pages Project

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Go to **Workers & Pages** → **Create application** → **Pages**
3. Click **Connect to Git**
4. Select the `braidMgr` repository from GitHub
5. Click **Begin setup**

### 2. Configure Build Settings

| Setting | Value |
|---------|-------|
| **Project name** | `braidmgr-docs` |
| **Production branch** | `main` |
| **Framework preset** | None |
| **Build command** | `pip install mkdocs-material && mkdocs build` |
| **Build output directory** | `site` |
| **Root directory** | `/` (repository root) |

### 3. Environment Variables (Optional)

No environment variables are required for the docs site.

### 4. Save and Deploy

Click **Save and Deploy**. Cloudflare will:
- Clone the repository
- Run the build command
- Deploy the `site/` directory to the edge network

### 5. Access Your Site

After deployment, your site will be available at:
- `https://braidmgr-docs.pages.dev` (default)
- Custom domain (if configured)

## Automatic Deployments

Once connected, Cloudflare Pages will automatically:
- Deploy on every push to `main` (production)
- Create preview deployments for pull requests

## Custom Domain (Optional)

To add a custom domain:
1. Go to your Pages project → **Custom domains**
2. Click **Set up a custom domain**
3. Enter your domain (e.g., `docs.braidmgr.com`)
4. Follow DNS configuration instructions

## Troubleshooting

### Build Fails with Python Error

Cloudflare Pages uses Python 3.7 by default. If you need a newer version:
1. Add a `.python-version` file to the repo root with content: `3.11`
2. Or set environment variable: `PYTHON_VERSION=3.11`

### MkDocs Not Found

Ensure the build command includes the pip install:
```bash
pip install mkdocs-material && mkdocs build
```

### Wrong Output Directory

Verify the build output directory is set to `site` (not `site/` or `./site`).

## Verification Checklist

- [ ] Site loads at `*.pages.dev` URL
- [ ] Navigation works correctly
- [ ] Search functionality works
- [ ] Light/dark mode toggle works
- [ ] All documentation pages render correctly
