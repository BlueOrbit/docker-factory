# Docker Factory

Automated Docker image factory for building and publishing multi-architecture images.

## Structure

```text
docker-factory/
├── images/           # Image definitions
├── scripts/          # Helper scripts
└── .github/          # CI/CD workflows
```

## Adding a New Image

1. Create a directory in `images/<name>`.
2. Add `Dockerfile`.
3. Add `image.yml` defining metadata.
4. Add source files in `src/`.

## Development

- **Build**: Handled by GitHub Actions.
- **Local Test**: `docker build -t test-image images/<name>`

## Configuration (`image.yml`)

```yaml
image_name: my-image
platforms:        # Platforms to build for
  - linux/amd64
  - linux/arm64
depends_on:       # Images this image depends on (triggers rebuilds)
  - base-image
```

