# Docker Factory 构建系统改进说明

## 改进日期
2026-01-15

## 背景
在原有实现中，GitHub Actions 使用 `strategy.matrix` 并行构建所有镜像，未考虑依赖顺序，导致依赖镜像可能在基础镜像构建完成前开始构建，引发构建失败。

## 核心问题

### 1. 构建顺序问题
- **问题**：`sharkdp-bat-1f9519d` 依赖 `sharkdp-bat`，但两者并行构建
- **后果**：依赖镜像可能在基础镜像推送前开始构建，导致 `FROM` 指令失败

### 2. PR 构建必败
- **问题**：原 `Wait for dependencies` 逻辑硬编码等待 `:latest` 标签
- **后果**：PR 构建不推送到 `:latest`，导致所有依赖任务超时失败

### 3. 资源浪费
- **问题**：基础镜像构建失败后，依赖镜像仍然等待 600 秒
- **后果**：浪费 GitHub Actions 并发配额

### 4. 校验不足
- **问题**：`lint_rules.py` 仅检查 `pre-build.sh` 配对，未校验关键文件
- **后果**：循环依赖、缺失文件等问题在运行时才暴露

## 改进方案

### 1. `scripts/generate_matrix.py` - 分层矩阵生成

#### 主要改进
- ✅ 使用 **Kahn 算法** 进行拓扑排序，生成分层构建矩阵
- ✅ 循环依赖检测改为 **严格模式**，检测到立即退出（`sys.exit(1)`）
- ✅ 输出格式从平坦列表改为分层结构

#### 输出示例
```json
{
  "layers": [
    {
      "layer": 0,
      "include": [
        {"name": "sharkdp-bat", "path": "images/sharkdp-bat", "platforms": "linux/amd64,linux/arm64"}
      ]
    },
    {
      "layer": 1,
      "include": [
        {"name": "sharkdp-bat-1f9519d", "path": "images/sharkdp-bat-1f9519d", "platforms": "linux/amd64,linux/arm64"}
      ]
    }
  ]
}
```

#### 优势
- **层内并行**：同一层的镜像可以并行构建（无相互依赖）
- **层间顺序**：下一层必须等待上一层完成
- **早期失败**：循环依赖在 CI 开始前就被检测并终止

---

### 2. `scripts/lint_rules.py` - 增强校验

#### 新增校验项
| 校验项 | 描述 |
|--------|------|
| ✅ Dockerfile 存在性 | 确保每个镜像目录包含 `Dockerfile` |
| ✅ image.yml 格式 | 校验 YAML 语法和必需字段 |
| ✅ image_name 一致性 | 确保 `image.yml` 中的 `image_name` 与目录名匹配 |
| ✅ 循环依赖检测 | 使用拓扑排序检测依赖环 |
| ✅ 不存在的依赖 | 检测 `depends_on` 中引用的镜像是否存在 |

#### 错误示例
```bash
[RULE VIOLATION] example-image: Dockerfile is missing.
[RULE VIOLATION] another-image: 'image.yml' has invalid YAML syntax: ...
[RULE VIOLATION] Circular dependency detected among images: image-a, image-b
[RULE VIOLATION] image-c: depends on non-existent image 'unknown'.
```

---

### 3. `.github/workflows/build-and-publish.yml` - 分层构建

#### 架构改进
- **移除**：Shell 脚本轮询 `docker manifest inspect` 的 `Wait for dependencies` 步骤
- **新增**：5 个独立的 layer job（`build-layer-0` 到 `build-layer-4`）
- **依赖链**：每层 job 使用 `needs` 等待上一层完成

#### Job 依赖关系
```
detect-changes
    ↓
build-layer-0  (无依赖的基础镜像)
    ↓
build-layer-1  (依赖 layer-0)
    ↓
build-layer-2  (依赖 layer-1)
    ↓
build-layer-3  (依赖 layer-2)
    ↓
build-layer-4  (依赖 layer-3)
```

#### 关键特性
1. **条件执行**：每层检查是否有镜像需要构建（`if: fromJson(...).include[0]`）
2. **失败快速中断**：上层失败，下层自动跳过（`needs.build-layer-X.result != 'failure'`）
3. **PR 友好**：不再依赖 `:latest` 标签，直接按层级顺序构建
4. **资源高效**：每层内并行，层间顺序，避免无效等待

---

## 测试验证

### 测试 1：分层矩阵生成
```bash
cd /Users/lanjiachen/Developer/BlueOrbit/docker-factory
python3 scripts/generate_matrix.py --all
```

**预期输出**：
- Layer 0 包含 `biomni`, `home-assistance`, `sharkdp-bat`, `spreadsheet`
- Layer 1 包含 `sharkdp-bat-1f9519d`

**实际结果**：✅ 通过

### 测试 2：校验规则
```bash
python3 scripts/lint_rules.py
```

**预期输出**：`All validation rules passed.`

**实际结果**：✅ 通过

---

## 局限性与未来改进

### 当前局限
1. **最大层数限制**：当前支持最多 5 层依赖（可扩展但需修改 workflow）
2. **静态 Job 定义**：GitHub Actions 不支持动态创建 job，需手动定义每层

### 未来改进方向
1. **动态层数支持**：探索使用 GitHub Actions 的 reusable workflow 或自定义 action
2. **并行度优化**：在同一层内，进一步按平台拆分并行任务
3. **缓存策略**：为每层设置独立的缓存 scope，提高缓存命中率

---

## 总结

通过本次改进，Docker Factory 构建系统实现了：
- ✅ **可靠性**：依赖顺序得到保障，循环依赖提前检测
- ✅ **效率**：失败快速中断，避免资源浪费
- ✅ **可维护性**：校验规则更全面，问题提前暴露
- ✅ **兼容性**：PR 构建正常工作，不再依赖 `:latest` 标签

构建顺序问题已从根本上解决。
