#!/bin/bash
# 面试虎 - 国产镜像源校验
# 原则6（强制）：所有 FROM/image 必须使用国产镜像源
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

errors=0

check_file() {
  local file="$1"
  local pattern="$2"
  while IFS= read -r line; do
    # 跳过注释和空行
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue
    # 检查是否使用国产源
    if ! echo "$line" | grep -qE '(docker\.m\.daocloud\.io|registry\.cn-hangzhou\.aliyuncs\.com|registry\.docker-cn\.com|ccr\.ccs\.tencentyun\.com)'; then
      echo "  ❌ 非国产源: $line" >&2
      errors=$((errors + 1))
    fi
  done < <(grep -E "$pattern" "$file")
}

echo "=== 面试虎 - 国产镜像源检查 ==="
echo ""

# 检查 Dockerfile
if [ -f "$PROJECT_DIR/backend/Dockerfile" ]; then
  echo "检查 backend/Dockerfile ..."
  check_file "$PROJECT_DIR/backend/Dockerfile" '^FROM '
fi

# 检查 docker-compose.yml 中的 image 字段
if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
  echo "检查 docker-compose.yml ..."
  check_file "$PROJECT_DIR/docker-compose.yml" 'image:'
fi

echo ""
if [ "$errors" -eq 0 ]; then
  echo "✅ 全部检查通过！所有镜像引用均使用国产源。"
else
  echo "❌ 发现 $errors 个非国产源引用，请修正后重试。"
  exit 1
fi
