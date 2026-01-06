# Git 远程仓库连接与提交指南

本指南主要介绍如何连接远程仓库、进行代码提交，以及关于 Docker Key 配置的说明。

## 1. 连接远程仓库

如果你是一个新的本地项目，需要关联到远程仓库（Github/Gitlab 等）：

```bash
# 初始化 git 仓库（如果尚未初始化）
git init

# 添加远程仓库地址
# 将 <URL> 替换为实际的仓库地址，例如 git@github.com:username/repo.git
git remote add origin <URL>

# 验证是否添加成功
git remote -v
```

如果你是直接克隆（Clone）下来的代码，则无需执行上述步骤，直接进入下一步。

## 2. 提交代码 (Commit)

提交代码分为“暂存”和“提交”两步。

### 第一步：暂存更改

```bash
# 添加所有更改到暂存区
git add .

# 或者只添加特定文件
git add path/to/file
```

### 第二步：提交更改

```bash
git commit -m "你的提交信息"
```

## 3. Commit Message 写作指南

为了保持提交历史清晰，建议遵循 **Conventional Commits** 规范。

**基本格式：**
```text
<类型>(<范围>): <描述>
```

**常用类型 (Type)：**
*   `feat`: 新功能 (feature)
*   `fix`: 修复 bug
*   `docs`: 文档变更
*   `style`: 代码格式调整（不影响代码运行的变动）
*   `refactor`: 代码重构（既不是新增功能，也不是修改 bug）
*   `perf`: 性能优化
*   `test`: 增加或修改测试
*   `chore`: 构建过程或辅助工具的变动

**示例：**
*   `feat: 添加用户登录功能`
*   `fix(auth): 修复 token 过期时间错误`
*   `docs: 更新 README 文档`
*   `chore: 更新依赖版本`

## 4. 推送代码 (Push)

```bash
# 第一次推送时，可能需要指定上游分支
git push -u origin main

# 后续推送
git push
```

## 5. 关于 Docker Key 配置

**对于本仓库 (docker-factory)：**

根据 `.github/workflows/build-and-publish.yml` 的配置，本项目使用的是 **GitHub Container Registry (ghcr.io)**，并且在 CI/CD 流程中使用了 GitHub 原生的 `${{ secrets.GITHUB_TOKEN }}` 进行身份验证。

```yaml
# 引用自 workflows 配置
username: ${{ github.actor }}
password: ${{ secrets.GITHUB_TOKEN }}
```

**结论：**
*   **你不需要** 手动配置 Docker Key 到仓库的 Secrets 中。
*   GitHub Actions 会自动使用临时的 `GITHUB_TOKEN` 来构建并推送镜像。
*   **注意**：确保仓库设置中，Workflow permissions 被设置为 "Read and write permissions"（通常在 Settings -> Actions -> General -> Workflow permissions 中配置），以便 Token 有权限推送到 Packages。
