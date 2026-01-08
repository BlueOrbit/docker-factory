# 基础镜像：官方镜像支持多架构，会自动切换
FROM python:3.12-slim-bookworm

# 环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    MPLBACKEND=Agg

WORKDIR /app

# 系统依赖：添加了 build-essential 以防某些 Python 包需要现场编译
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tmux \
    asciinema \
    procps \
    build-essential \
    libatlas-base-dev \
    gfortran \
    fonts-wqy-zenhei \
    graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/local/bin/python3 /usr/local/bin/python

# 安装 uv：自动匹配目标平台的 uv 架构
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 安装 Python 依赖：在 ARM 模拟环境下，uv 会优先下载预编译的 wheel，
# 如果没有 wheel，它会利用上面的 build-essential 进行编译。
RUN uv pip install --no-cache \
    "pytest>=8.4.1" \
    "pytest-json-ctrf>=0.3.5" \
    "numpy>=1.26.4,<2.0.0" \
    "pandas>=2.2.1" \
    "matplotlib>=3.8.3" \
    "seaborn>=0.13.2" \
    "scipy>=1.12.0" \
    "scikit-learn>=1.4.0,<1.5.0" \
    "openpyxl>=3.1.2" \
    "requests>=2.32.3,<3.0.0"

# 保持默认 CMD 或 ENTRYPOINT