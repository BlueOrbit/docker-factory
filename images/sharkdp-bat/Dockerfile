# A minimal, stable Linux environment for Rust projects like sharkdp/bat
FROM debian:bookworm-slim

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
# - python3: occasionally used by project scripts/tests (safe to include)
# - tzdata: avoids timezone-related prompts/tools
RUN --mount=type=cache,target=/var/cache/apt \
    set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      build-essential \
      pkg-config \
      libssl-dev \
      python3 \
      tzdata \
    ; \
    rm -rf /var/lib/apt/lists/*

# ---- Rust toolchain ----
# Pin toolchain for determinism (adjust if your dataset standardizes a different version).
# bat v0.22.0 should build fine on stable; 1.70+ is generally safe on bookworm.
ARG RUST_TOOLCHAIN=1.74.1

RUN set -eux; \
    mkdir -p "${CARGO_HOME}" "${RUSTUP_HOME}"; \
    curl -fsSL https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal --default-toolchain "${RUST_TOOLCHAIN}"; \
    rustup --version; \
    rustc --version; \
    cargo --version

# Create a non-root user (many benches prefer this)
RUN set -eux; \
    useradd -m -u 1000 -s /bin/bash runner; \
    mkdir -p /work; \
    chown -R runner:runner /work /opt/cargo /opt/rustup

USER runner
WORKDIR /work

# Helpful defaults for consistent logs/output
ENV TERM=xterm-256color \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Entrypoint intentionally omitted; evaluation harness should run commands explicitly.
