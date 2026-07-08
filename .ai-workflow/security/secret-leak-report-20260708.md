# 密钥泄露扫描报告

> 扫描时间：2026-07-08T05:54:58.558860+00:00
> 项目路径：/Users/siyuan/Documents/www/ai-project/interview-tiger

## 统计概览

| 指标 | 数值 |
|------|------|
| 扫描文件数 | 88 |
| 跳过文件数 | 1328 |
| 发现泄露 | **296** |
| 🔴 CRITICAL | 5 |
| 🟠 HIGH | 13 |
| 🟡 MEDIUM | 278 |
| 🔵 LOW | 0 |

---

## 🔴 CRITICAL 风险（需立即修复）

### 数据库连接串含密码

| 文件 | 行号 | 风险描述 |
|------|------|----------|
| `docker-compose.yml` | 56 | 数据库连接串中硬编码密码 |
| `start.sh` | 167 | 脚本中硬编码数据库密码 |
| `backend/config.py` | 45 | 配置文件中硬编码数据库连接串 |
| `backend/.env` | 33 | 环境变量文件中硬编码数据库密码 |
| `docs/部署指南.md` | 82 | 文档中包含数据库连接串密码 |

**修复建议：**
- 将数据库密码移至环境变量或外部密钥管理服务
- 敏感文档中的密码应使用占位符

---

## 🟠 HIGH 风险（建议尽快修复）

### API Key 硬编码

| 文件 | 行号 | 风险描述 |
|------|------|----------|
| `backend/app/routes/config.py` | 64, 66 | 代码中硬编码API Key变量名 |
| `docs/字节跳动接口调用指南.md` | 308, 348, 405, 496, 501 | 文档中包含API_KEY示例 |
| `scripts/backend/tests/scene_s2_config.py` | 49 | 测试脚本中硬编码API Key |
| `scripts/backend/tests/scene_s3_question.py` | 16, 41 | 测试脚本中硬编码API Key |
| `scripts/backend/tests/scene_s5_generate.py` | 16, 41, 55 | 测试脚本中硬编码API Key |

**修复建议：**
- 将API Key移至环境变量，切勿硬编码在代码中
- 测试脚本应使用环境变量或配置文件

---

## 🟡 MEDIUM 风险（可按需处理）

### 内网IP地址暴露

| 文件 | 行号 | 匹配内容 |
|------|------|----------|
| `docker-compose.yml` | 6, 14, 47, 89 | Docker网络配置中的内网IP |

### 高熵字符串检测（大部分为误报）

278条MEDIUM级别告警中，大部分是中文错误提示、URL、CSS类名、日志模板字符串等正常代码内容，**建议忽略**。

---

## Git 历史泄露检查

### 敏感文件追踪

- **已跟踪敏感文件**: 无
- **历史泄露文件**: 无

### .gitignore 缺失规则

| 缺失规则 | 说明 |
|----------|------|
| `*.pem` | 证书文件 |
| `*.key` | 密钥文件 |
| `*.p12` | PKCS#12证书 |
| `*.pfx` | PFX证书 |
| `credentials*.json` | 凭据文件 |
| `service-account*.json` | 服务账号文件 |
| `secrets*.yml`, `secrets*.yaml` | 密钥配置文件 |
| `id_rsa*` | SSH私钥 |
| `*.keystore` | Java密钥库 |

---

## 修复优先级建议

| 优先级 | 修复项 | 原因 |
|--------|--------|------|
| P0 | `.env` 文件添加到 `.gitignore` | 防止敏感配置泄露到仓库 |
| P0 | 移除代码/文档中的硬编码密码 | 直接安全风险 |
| P1 | 补充 `.gitignore` 缺失规则 | 预防未来泄露 |
| P1 | 测试脚本使用环境变量 | 避免测试数据泄露 |
| P2 | 清理文档中的API Key示例 | 文档安全 |
