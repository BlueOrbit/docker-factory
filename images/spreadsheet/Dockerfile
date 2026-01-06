# -----------------------------------------------------------------------------
# Base Image: 使用官方轻量级 Python 3.11 (基于 Debian 12 Bookworm)
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm

# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------
LABEL maintainer="TerminalBench-Builder-Lan"
LABEL description="Docker image for SpreadsheetBench reproduction with uv package manager"

# -----------------------------------------------------------------------------
# Environment Variables (环境变量配置)
# -----------------------------------------------------------------------------
# 防止 Python 生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE=1
# 确保控制台输出不被缓存
ENV PYTHONUNBUFFERED=1
# 定义虚拟环境路径
ENV VIRTUAL_ENV=/opt/venv
# 将虚拟环境的 bin 目录加入 PATH，确保后续直接使用 python/pip 命令时指向该环境
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# -----------------------------------------------------------------------------
# Workspace Setup (工作目录配置)
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# System Dependencies (系统工具安装)
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git vim procps tmux asciinema ca-certificates \
    libreoffice-calc-nogui libreoffice-core-nogui \
    fontconfig fonts-dejavu-core \
    default-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Install uv (安装 uv 包管理器)
# -----------------------------------------------------------------------------
# 从官方镜像中提取 uv 二进制文件，这是最安全快捷的方式
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# -----------------------------------------------------------------------------
# Python Dependencies (Python 依赖安装)
# -----------------------------------------------------------------------------
# 1. 创建虚拟环境
RUN uv venv $VIRTUAL_ENV

# 2. 安装指定的依赖库
# 使用 --no-cache 防止缓存占用空间
# spreadsheet-deps: pandas, openpyxl, xlsxwriter, xlrd, odfpy
# science-deps: numpy, scipy, matplotlib
# utility-deps: requests, tabulate
RUN uv pip install --no-cache \
    pandas \
    openpyxl \
    xlsxwriter \
    xlrd \
    odfpy \
    numpy \
    scipy \
    matplotlib \
    requests \
    tabulate

RUN uv pip install --no-cache \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5


