FROM ghcr.io/blueorbit/docker-factory/sharkdp-bat:latest

# Switch to specific commit version for reproducibility
WORKDIR /app

RUN set -eux && \
    git checkout 1f9519d8b9bd3efac979766eefa0c6fae594b984 && \
    git clean -fd

# Install Python dependencies using uv (consistent with base image)
RUN uv pip install --no-cache swe-rex

# Create required directories for logs and test results
RUN mkdir -p /logs /app/test/results
