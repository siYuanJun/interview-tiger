# 贡献指南

感谢你对面试虎的关注和贡献意愿！以下指南帮助你快速上手。

## 行为准则

- 友善包容地对待每一位贡献者
- 建设性地提出意见，对事不对人
- 尊重不同的技术选择和观点
- 帮助新手成长，分享知识

## 我能做什么？

### 🐛 报告 Bug

在 [Issues](https://github.com/siYuanJun/interview-tiger/issues) 提交 Bug 时，请包含：

- **环境信息**：操作系统、Docker 版本、浏览器版本
- **复现步骤**：清晰描述触发 Bug 的操作流程
- **期望行为**：你期望发生什么
- **实际行为**：实际发生了什么
- **截图/日志**：尽可能提供错误截图或控制台日志

### 💡 功能建议

- 先在 Issues 中搜索是否已有人提出相同建议
- 描述功能的使用场景和价值
- 如果是复杂的特性，可附上简单的设计方案

### 🔧 提交代码

1. **Fork** 本仓库
2. 从 `master` 分支创建你的特性分支：`git checkout -b feature/xxx`
3. 编写代码并确保通过现有测试
4. 提交前运行 `docker-compose up --build` 确认服务正常启动
5. 推送并创建 Pull Request

### 分支命名规范

- `feature/xxx` — 新功能
- `fix/xxx` — Bug 修复
- `docs/xxx` — 文档更新
- `refactor/xxx` — 代码重构

### Commit 规范

遵循 Conventional Commits：

```
feat: 添加英文面试场景 Prompt 模板
fix: 修复 Safari 下 Web Speech API 兼容性问题
docs: 更新部署文档中的环境变量说明
refactor: 重构知识库提供者工厂函数
```

## 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/siYuanJun/interview-tiger.git
cd interview-tiger

# 2. 复制环境变量
cp backend/.env.example backend/.env
# 编辑 .env 填入你的火山引擎 API Key

# 3. 启动服务
docker-compose up --build -d

# 4. 访问
# 前端：http://localhost:40003
# 后端 API：http://localhost:8001
# 健康检查：http://localhost:8001/api/health
```

## 代码规范

### 后端 (Python)

- 遵循 PEP 8
- 使用类型注解
- 新增路由需要添加对应的测试用例
- 服务类遵循 `KnowledgeProvider` 的接口设计模式

### 前端 (Vue 3 / TypeScript)

- 使用 Composition API
- 组件命名使用 PascalCase
- 样式优先使用 Tailwind CSS 工具类
- 状态管理使用 Pinia

## Good First Issues

标记为 `good first issue` 的 Issue 专门留给新贡献者，是入门的最佳选择。

常见入门任务：
- 优化 Prompt 模板的措辞
- 添加文档翻译
- 补充单元测试
- 修复样式小问题

## Pull Request 审核

- 所有 PR 至少需要一位维护者审核
- CI 通过后方可合并
- PR 描述中请关联相关 Issue

## 许可证

贡献的代码将同样以 AGPL-3.0 协议发布。请确保你有权将代码以该协议贡献。
