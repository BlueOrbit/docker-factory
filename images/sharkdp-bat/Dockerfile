# A minimal, stable Linux environment for Rust projects like sharkdp/bat
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive \
    # Make Rust builds more reproducible and less flaky in CI-like environments
    CARGO_INCREMENTAL=0 \
    RUST_BACKTRACE=1 \
    # Avoid interactive tz prompts
    TZ=Etc/UTC \
    # Keep cargo home in a predictable location
    CARGO_HOME=/opt/cargo \
    RUSTUP_HOME=/opt/rustup \
    PATH=/opt/cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# ---- System deps ----
# - build-essential, pkg-config: for compiling crates with native deps
# - libssl-dev, ca-certificates: common native deps + HTTPS for cargo
# - git: fetch repo
# - curl: install rustup
# - tzdata: avoids timezone-related prompts/tools
# Note: Python is already included in the base image (python:3.12-slim-bookworm)
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      build-essential \
      pkg-config \
      libssl-dev \
      tzdata \
      zlib1g-dev \     
      libonig-dev \    
    ; \
    rm -rf /var/lib/apt/lists/*

# ---- Install uv for Python package management ----
# Install uv: automatically matches target platform architecture
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# ---- Install Python test dependencies ----
# Pre-install test dependencies to avoid installing them in test scripts
ENV UV_SYSTEM_PYTHON=1
RUN uv pip install --no-cache \
    "pytest>=8.4.1" \
    "pytest-json-ctrf>=0.3.5"

# ---- Rust toolchain ----
# Pin toolchain for determinism (adjust if your dataset standardizes a different version).
# bat requires rust 1.87+ according to Cargo.toml
ARG RUST_TOOLCHAIN=stable

RUN set -eux; \
    rm -rf "${CARGO_HOME}" "${RUSTUP_HOME}"; \
    mkdir -p "${CARGO_HOME}" "${RUSTUP_HOME}"; \
    curl -fsSL https://sh.rustup.rs | sh -s -- -y \
      --no-modify-path \
      --profile minimal \
      --default-toolchain "${RUST_TOOLCHAIN}"; \
    /opt/cargo/bin/rustup --version; \
    /opt/cargo/bin/rustc --version; \
    /opt/cargo/bin/cargo --version


# Helpful defaults for consistent logs/output
ENV TERM=xterm-256color \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN cd /app && git clone https://github.com/sharkdp/bat.git .

RUN git checkout 1f9519d8b9bd3efac979766eefa0c6fae594b984

# RUN cargo install git-delta --locked

# Entrypoint intentionally omitted; evaluation harness should run commands explicitly.
