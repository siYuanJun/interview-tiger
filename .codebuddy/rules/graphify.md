# graphify 知识图谱使用规则

当需要分析项目结构、模块依赖、调用链路、影响面评估时，**优先使用 graphify 知识图谱**而非逐文件读取源码。

## 图谱位置
- `graphify-out/graph.json` — 主图谱（2517 节点，2618 边，193 社区）
- `graphify-out/GRAPH_REPORT.md` — 详细报告
- `graphify-out/graph.html` — 交互式可视化

## 何时使用
- 问「X 模块涉及哪些文件」→ 扫 `graph.json` 的 nodes/links
- 问「改了 A 会影响什么」→ 查节点 A 的出边
- 问「A 和 B 什么关系」→ `graphify path "A" "B"`
- 问「解释某个组件/函数」→ `graphify explain "名称"`
- 做影响评估时 → 先用 graphify 扫依赖面，再读关键文件

## 使用方式
```bash
# CLI 查询
uv tool run --from graphifyy graphify explain "节点名"
uv tool run --from graphifyy graphify path "A" "B"

# Python 直接读 JSON
python3 -c "
import json
with open('graphify-out/graph.json') as f:
    g = json.load(f)
# nodes = g['nodes'], links = g['links']
"
```

## 更新图谱
代码变更后运行（免费，无需 API Key）：
```bash
uv tool run --from graphifyy graphify update .
```
