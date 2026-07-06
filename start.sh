#!/bin/bash

set -e

PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PORT=8001

echo "======================================"
echo "         面试虎 - 快速启动脚本"
echo "======================================"
echo ""

show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  docker      使用Docker Compose启动全部服务（推荐）"
    echo "  backend     本地启动后端服务（需先启动数据库）"
    echo "  frontend    本地启动前端服务"
    echo "  all         本地启动前后端（需先启动数据库）"
    echo "  db          启动PostgreSQL数据库（Docker容器）"
    echo "  stop        停止所有服务"
    echo "  logs        查看后端日志"
    echo "  status      查看服务状态"
    echo "  help        显示此帮助信息"
    echo ""
    echo "推荐使用:"
    echo "  $0 docker     # 一键启动全部服务（含数据库）"
    echo ""
    echo "本地开发:"
    echo "  $0 db         # 先启动数据库"
    echo "  $0 all        # 再启动前后端"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker 未安装，请先安装 Docker Desktop"
        echo "   下载地址: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo "❌ Docker 未运行，请启动 Docker Desktop"
        exit 1
    fi
}

check_port() {
    local port=$1
    if lsof -Pi ":$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

kill_port() {
    local port=$1
    local pids=$(lsof -Pi ":$port" -sTCP:LISTEN -t 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "⚠️  端口 $port 被占用，正在清理..."
        kill -9 $pids 2>/dev/null || true
        sleep 1
    fi
}

start_backend() {
    echo "🚀 启动后端服务..."
    cd "$BACKEND_DIR"
    
    if [ ! -f ".env" ]; then
        echo "⚠️  .env 文件不存在，正在创建..."
        cp .env.example .env
    fi
    
    if ! check_port 5432; then
        echo "⚠️  PostgreSQL 数据库未启动，正在启动..."
        start_db
        sleep 5
    fi
    
    kill_port $BACKEND_PORT
    
    echo "📦 安装依赖..."
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    
    echo "🔧 启动 uvicorn..."
    python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload
}

start_frontend() {
    echo "🚀 启动前端服务..."
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        echo "📦 安装依赖..."
        npm install
    fi
    
    echo "🔧 启动 Vite..."
    npm run dev
}

start_all() {
    echo "🚀 本地启动全部服务..."
    
    echo "📦 检查后端依赖..."
    cd "$BACKEND_DIR"
    if [ ! -f ".env" ]; then
        cp .env.example .env
    fi
    
    echo "📦 安装后端依赖..."
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt > /dev/null 2>&1 || true
    
    echo "📦 检查前端依赖..."
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ]; then
        npm install > /dev/null 2>&1 || true
    fi
    
    if ! check_port 5432; then
        echo "⚠️  PostgreSQL 数据库未启动，正在启动..."
        start_db
        sleep 5
    fi
    
    kill_port $BACKEND_PORT
    
    echo ""
    echo "✨ 后端服务启动在: http://localhost:$BACKEND_PORT"
    echo "✨ 前端服务启动在: http://localhost:5173"
    echo "✨ PostgreSQL: localhost:5432"
    echo ""
    echo "按 Ctrl+C 停止服务"
    
    cd "$BACKEND_DIR"
    python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    BACKEND_PID=$!
    
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '🛑 服务已停止'" INT
    
    wait
}

start_db() {
    echo "🚀 启动 PostgreSQL 数据库（Docker容器）..."
    check_docker
    
    echo "📦 检查/创建数据目录..."
    mkdir -p "$PROJECT_DIR/data/postgres"
    
    echo "� 清理旧容器..."
    docker rm -f interview-tiger-db 2>/dev/null || true
    
    echo "�🚀 启动 PostgreSQL 容器..."
    docker run -d \
        --name interview-tiger-db \
        --network=bridge \
        -p 5432:5432 \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=password \
        -e POSTGRES_DB=interview_tiger \
        -e TZ=Asia/Shanghai \
        -v "$PROJECT_DIR/data/postgres:/var/lib/postgresql/data" \
        --restart unless-stopped \
        docker.m.daocloud.io/library/postgres:15
    
    echo "⏳ 等待数据库启动..."
    timeout=30
    count=0
    while [ $count -lt $timeout ]; do
        if docker exec interview-tiger-db pg_isready -U postgres > /dev/null 2>&1; then
            break
        fi
        count=$((count+1))
        sleep 1
    done
    
    if [ $count -ge $timeout ]; then
        echo "❌ 数据库启动超时"
        exit 1
    fi
    
    echo ""
    echo "✨ PostgreSQL 启动成功!"
    echo "   端口: 5432"
    echo "   数据库: interview_tiger"
    echo "   用户: postgres"
    echo "   密码: password"
}

start_docker() {
    echo "🚀 使用 Docker Compose 启动全部服务..."
    check_docker
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ docker-compose 未安装"
        echo "   安装命令: pip install docker-compose"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    
    if [ ! -f "backend/.env" ]; then
        echo "⚠️  .env 文件不存在，正在创建..."
        cp backend/.env.example backend/.env
    fi
    
    echo "📦 构建并启动容器..."
    docker-compose up --build -d
    
    echo ""
    echo "⏳ 等待服务启动..."
    sleep 10
    
    echo ""
    echo "✨ 服务启动成功!"
    echo ""
    echo "服务列表:"
    echo "  🚀 后端 API: http://localhost:8001"
    echo "  🐘 PostgreSQL: localhost:5432"
    echo ""
    echo "查看日志: $0 logs"
    echo "停止服务: $0 stop"
}

stop_services() {
    echo "🛑 停止所有服务..."
    
    cd "$PROJECT_DIR"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down 2>/dev/null || true
    fi
    
    docker stop interview-tiger-db 2>/dev/null || true
    docker stop interview-tiger-backend 2>/dev/null || true
    
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo "✅ 所有服务已停止"
}

show_logs() {
    echo "📋 查看后端日志..."
    cd "$PROJECT_DIR"
    
    if command -v docker-compose &> /dev/null && docker-compose ps 2>/dev/null | grep -q "running"; then
        docker-compose logs -f backend
    elif docker ps 2>/dev/null | grep -q "interview-tiger-backend"; then
        docker logs -f interview-tiger-backend
    else
        echo "⚠️  后端容器未运行"
    fi
}

show_status() {
    echo "📊 服务状态..."
    
    echo ""
    echo "=== Docker 服务 ==="
    if command -v docker &> /dev/null; then
        docker ps --filter "name=interview-tiger" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "无运行中的容器"
    else
        echo "Docker 未安装"
    fi
    
    echo ""
    echo "=== 本地服务 ==="
    if check_port $BACKEND_PORT; then
        echo "✅ 后端 API: http://localhost:$BACKEND_PORT"
    else
        echo "❌ 后端 API: 未运行"
    fi
    
    if check_port 5173; then
        echo "✅ 前端服务: http://localhost:5173"
    else
        echo "❌ 前端服务: 未运行"
    fi
    
    if check_port 5432; then
        echo "✅ PostgreSQL: localhost:5432"
    else
        echo "❌ PostgreSQL: 未运行"
    fi
}

case "${1:-help}" in
    docker)
        start_docker
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        start_all
        ;;
    db)
        start_db
        ;;
    stop)
        stop_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    help)
        show_help
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
