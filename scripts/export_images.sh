#!/bin/bash
# 面试虎 - 镜像导出脚本
# 原则5：统一镜像导出，按服务名选择
# 用法: bash scripts/export_images.sh [backend|all]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

export_one() {
  local service="$1"
  local image=$(docker compose -f "$PROJECT_DIR/docker-compose.yml" images -q "$service" 2>/dev/null)
  if [ -z "$image" ]; then
    echo "镜像 $service 不存在，请先执行 docker compose build $service" >&2
    return 1
  fi
  echo "导出 $service ..."
  docker save -o "$PROJECT_DIR/scripts/${service}.tar" "$image"
  echo "完成: scripts/${service}.tar"
}

case "${1:-all}" in
  backend) export_one "backend" ;;
  all)    export_one "backend" ;;
  *)      echo "用法: export_images.sh [backend|all]" >&2; exit 1 ;;
esac
