# 面试虎后端接口回归测试

## 简介

本测试套件用于对面试虎后端服务进行接口回归测试，包含业务流程测试和参数校验测试。

## 测试场景

| 场景 | 文件 | 测试内容 |
|------|------|----------|
| S1 | scene_s1_health_check.py | 健康检查接口 |
| S2 | scene_s2_config.py | 配置管理接口（GET/POST） |
| S3 | scene_s3_question.py | 问题处理接口（核心API） |
| S4 | scene_s4_search.py | 知识库检索接口 |
| S5 | scene_s5_generate.py | 大模型生成接口 |
| S6 | scene_s6_transcript.py | 对话转录接口 |
| S7 | scene_s7_dialogue.py | 对话管理接口（CRUD） |

## 运行方式

### 全量回归测试

```bash
./run_all.sh
```

### 仅运行 P0 场景

```bash
./run_p0.sh
```

### 手动运行

```bash
cd tests
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 全量测试
python main.py

# 仅P0场景
python main.py --p0
```

## 配置说明

配置文件 `config.py`:

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| BASE_URL | http://localhost:8001 | 后端服务地址 |
| TIMEOUT | 30 | 请求超时时间（秒） |

## 测试特点

- **命令行可视化**: 显示时间戳、步骤序号、请求方法/URL、参数、HTTP状态、业务状态、耗时、响应数据
- **致命错误即停**: 前置失败导致后续无法进行时，立即退出
- **独立日志文件**: `logs/test_{时间戳}.log`，内容与终端输出一致
- **venv隔离**: 使用 Python 虚拟环境，不污染系统全局 pip

## 日志文件

测试日志保存在 `logs/` 目录下，命名格式: `test_YYYY-MM-DD_HH-MM-SS.log`

## 依赖

- Python 3.8+
- requests 2.32.0
