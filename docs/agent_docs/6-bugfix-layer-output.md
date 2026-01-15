# Bug Fix: Layer 输出格式错误

## 问题发现
2026-01-15 测试 push 时发现 GitHub Actions 失败。

### 错误信息
```
Error when evaluating 'strategy' for job 'build-layer-0'. 
.github/workflows/build-and-publish.yml (Line: 102, Col: 15): 
Unexpected value '0'
```

**错误链接**：https://github.com/BlueOrbit/docker-factory/actions/runs/21021757833

## 根本原因

### 问题分析
`generate_matrix.py` 生成的 JSON 结构为：
```json
{
  "layers": [
    {
      "layer": 0,
      "include": [...]
    },
    {
      "layer": 1,
      "include": [...]
    }
  ]
}
```

在 workflow 的 `Detect Changed Images` 步骤中，使用以下命令提取每层数据：
```bash
LAYER_MATRIX=$(echo "$LAYERED_JSON" | jq -c ".layers[$i] // {\"include\": []}")
```

这会提取整个 layer 对象，包括 `layer` 字段：
```json
{
  "layer": 0,
  "include": [...]
}
```

然而，GitHub Actions 的 `strategy.matrix` 只接受以下格式：
```json
{
  "include": [...]
}
```

当 `strategy.matrix` 遇到额外的 `layer: 0` 字段时，会报错 "Unexpected value '0'"。

## 修复方案

### 修改位置
`.github/workflows/build-and-publish.yml` - `Detect Changed Images` 步骤

### 修改前
```bash
for i in {0..4}; do
  LAYER_MATRIX=$(echo "$LAYERED_JSON" | jq -c ".layers[$i] // {\"include\": []}")
  echo "layer-$i=$LAYER_MATRIX" >> $GITHUB_OUTPUT
  echo "Layer $i: $LAYER_MATRIX"
done
```

### 修改后
```bash
for i in {0..4}; do
  LAYER_MATRIX=$(echo "$LAYERED_JSON" | jq -c "if .layers[$i] then {\"include\": .layers[$i].include} else {\"include\": []} end")
  echo "layer-$i=$LAYER_MATRIX" >> $GITHUB_OUTPUT
  echo "Layer $i: $LAYER_MATRIX"
done
```

### 关键改动
使用 `jq` 的条件表达式，只提取 `include` 字段：
- 如果层存在：`{"include": .layers[$i].include}`
- 如果层不存在：`{"include": []}`

## 验证结果

### 测试 1：Layer 0 输出
```bash
$ python3 scripts/generate_matrix.py --all | \
  jq -c 'if .layers[0] then {"include": .layers[0].include} else {"include": []} end'

# 输出（格式化后）：
{
  "include": [
    {"name": "biomni", "path": "images/biomni", "platforms": "linux/amd64,linux/arm64"},
    {"name": "home-assistance", "path": "images/home-assistance", "platforms": "linux/amd64,linux/arm64"},
    {"name": "sharkdp-bat", "path": "images/sharkdp-bat", "platforms": "linux/amd64,linux/arm64"},
    {"name": "spreadsheet", "path": "images/spreadsheet", "platforms": "linux/amd64,linux/arm64"}
  ]
}
```
✅ 格式正确

### 测试 2：Layer 1 输出
```bash
$ python3 scripts/generate_matrix.py --all | \
  jq -c 'if .layers[1] then {"include": .layers[1].include} else {"include": []} end'

# 输出：
{
  "include": [
    {"name": "sharkdp-bat-1f9519d", "path": "images/sharkdp-bat-1f9519d", "platforms": "linux/amd64,linux/arm64"}
  ]
}
```
✅ 格式正确

### 测试 3：不存在的层
```bash
$ python3 scripts/generate_matrix.py --all | \
  jq -c 'if .layers[5] then {"include": .layers[5].include} else {"include": []} end'

# 输出：
{"include":[]}
```
✅ 返回空数组

### 测试 4：空数组的条件判断
```bash
$ echo '{"include":[]}' | jq -c '.include[0]'

# 输出：
null
```
✅ 在 GitHub Actions 的 `if` 条件中会被判定为 false，不会执行 job

## 影响范围
- 所有分层 job（`build-layer-0` 到 `build-layer-4`）
- 不影响其他逻辑

## 状态
✅ 已修复
✅ 已验证
🚀 可以重新 push 测试

## 后续建议
1. 重新 push 代码触发 CI 构建
2. 观察各层 job 的执行顺序
3. 确认依赖关系正确生效
