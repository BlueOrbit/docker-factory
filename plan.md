# Docker Factory Implementation Plan

## 1. 目标与范围（Goals & Scope）

本项目旨在构建一个 **`docker-factory` 单一仓库（monorepo）**，用于**自动化构建、发布和维护多类别、多架构（amd64 / arm64）的 Docker 镜像**。

核心目标：

* 支持 **多个镜像类别**（如 `biomini`、`spreadsheet`），统一构建体系
* 支持 **多架构镜像（multi-arch manifest）**
* 支持 **自动变更检测 + 并行构建**
* 支持 **版本化发布（Git tag）与持续集成发布（main）**
* 确保 **可复现、可扩展、可维护**

---

## 2. 仓库结构与总体架构

采用 **monorepo + 镜像隔离上下文** 的结构，每个镜像拥有独立目录与构建上下文，但共享统一 CI/CD 系统。

### 2.1 目录结构

```text
docker-factory/
├── .github/
│   └── workflows/
│       ├── build-and-publish.yml   # 主 CI/CD：检测、构建、发布
│       └── manual-release.yml      # （可选）手动/特殊发布流程
│
├── images/
│   ├── biomini/
│   │   ├── Dockerfile
│   │   ├── image.yml               # 镜像元数据与依赖声明
│   │   ├── pre-build.sh             # （可选）宿主侧预处理脚本
│   │   └── src/                     # 构建上下文
│   │
│   └── spreadsheet/
│       ├── Dockerfile
│       ├── image.yml
│       └── src/
│
├── scripts/
│   └── helpers.sh                   # CI/CD 共享辅助脚本
│
├── plan.md                          # 本文件
└── README.md
```

---

## 3. 镜像元数据与依赖声明（image.yml）

为避免在 CI 中硬编码规则，每个镜像目录包含一个 `image.yml`，用于描述构建元信息。

### 3.1 image.yml 示例

```yaml
image_name: biomini
platforms:
  - linux/amd64
  - linux/arm64
depends_on: []
```

```yaml
image_name: spreadsheet
platforms:
  - linux/amd64
  - linux/arm64
depends_on:
  - biomini
```

用途：

* 决定最终镜像名称
* 控制支持的平台
* 明确镜像间依赖关系，用于触发**依赖传播重建**

---

## 4. 镜像命名与 Registry 策略

### 4.1 Registry 选择

**默认：GitHub Container Registry (GHCR)**

* 使用 `GITHUB_TOKEN` 无需额外凭据
* 与 GitHub Actions 深度集成
* 支持私有/公开镜像

镜像命名规范：

```text
ghcr.io/<org>/<image_name>:<tag>
```

示例：

```text
ghcr.io/example-org/biomini:latest
ghcr.io/example-org/spreadsheet:sha-a1b2c3d
```

---

## 5. 版本与 Tag 策略（关键决策）

### 5.1 main 分支（持续集成发布）

每次 push 到 `main`：

* 构建 **发生变更的镜像**
* 推送以下 tag：

  * `:sha-<git-sha>`
  * `:main`
  * （可选）`:latest`（默认开启，用于内部消费）

> `latest` 在 main 分支代表 **“main 的最新状态”**

---

### 5.2 Git Tag 发布（版本发布）

当 push Git tag（如 `v1.2.3`）时：

* **强制构建并发布所有镜像（无论是否发生变更）**
* 所有镜像统一使用该版本号，确保版本一致性
* 推送 tag：

  * `:v1.2.3`
  * `:v1.2`
  * `:v1`
  * `:latest`（明确指向最新稳定版本）

> **结论性决策**：
> **tag 触发 = 全量构建 + 全量发布**

---

## 6. CI/CD 工作流设计（build-and-publish.yml）

### 6.1 触发条件

```yaml
on:
  push:
    branches: [ main ]
    paths:
      - "images/**"
  push:
    tags:
      - "v*"
  workflow_dispatch:
```

---

### 6.2 Workflow 权限（GHCR 必须）

```yaml
permissions:
  contents: read
  packages: write
```

---

### 6.3 Job 1：Detect Changes

职责：

* 使用 `dorny/paths-filter` 检测哪些 `images/<name>` 发生变更
* 解析对应 `image.yml`
* 根据 `depends_on` 生成 **最终构建列表（含依赖传播）**
* 在 tag 触发时，直接返回 **全部镜像**

输出：

```json
{
  "matrix": [
    { "name": "biomini", "path": "images/biomini" },
    { "name": "spreadsheet", "path": "images/spreadsheet" }
  ]
}
```

---

### 6.4 Job 2：Build & Push（Matrix）

#### 核心 Actions

* `docker/setup-qemu-action@v3`
* `docker/setup-buildx-action@v3`
* `docker/login-action@v3`
* `docker/metadata-action@v5`
* `docker/build-push-action@v6`

#### 关键配置点

* **平台**：来自 `image.yml`
* **构建上下文**：`images/<name>`
* **缓存隔离**：

```yaml
cache-from: type=gha,scope=${{ matrix.name }}
cache-to: type=gha,scope=${{ matrix.name }},mode=max
```

避免不同镜像互相污染缓存。

---

### 6.5 PR 行为（安全策略）

* PR 仅执行 build（`push: false`）
* 不推送镜像
* 不暴露 registry 凭据

---

## 7. 多架构支持（Multi-Architecture）

* 架构：`linux/amd64`, `linux/arm64`
* 使用 QEMU 进行交叉构建
* 输出 **单一 multi-arch manifest**

构建后校验（CI 内）：

```bash
docker buildx imagetools inspect ghcr.io/<org>/<image>:<tag>
```

---

## 8. pre-build.sh 使用规范

`pre-build.sh` 仅用于：

* **必须在宿主环境执行的预计算**
* 输出结果必须落在镜像构建上下文内
* 脚本应 **幂等、可重复执行**

推荐优先方案：
➡️ 能放进 Dockerfile 的，一律放进 Dockerfile（可缓存、可复现）

---

## 9. 实施步骤（Roadmap）

1. 初始化仓库与目录结构
2. 为每个镜像添加 `Dockerfile + image.yml`
3. 实现 `Detect Changes` 逻辑（含依赖传播）
4. 完成 build-and-publish.yml
5. 验证：

   * main 分支单镜像变更
   * tag 触发全量发布
   * multi-arch manifest 正确
6. 文档完善（README）

