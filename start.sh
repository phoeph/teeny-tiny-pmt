#!/bin/bash

# 项目一键启动脚本
# 作者: Assistant
# 日期: 2025-12-17

# 解析命令行参数
QUICK_MODE=false
NO_MONITOR=false

for arg in "$@"; do
    if [ "$arg" = "--quick" ] || [ "$arg" = "-q" ]; then
        QUICK_MODE=true
    elif [ "$arg" = "--print" ] || [ "$arg" = "-p" ]; then
        NO_MONITOR=true
    fi
done

if [ "$QUICK_MODE" = true ]; then
    echo "🚀 快速启动模式..."
else
    echo "🚀 开始启动项目管理系统..."
fi

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查是否已有进程在运行
FRONTEND_PORT=8080
BACKEND_PORT=8000

echo "🔍 检查端口占用情况..."
FRONTEND_PID=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
BACKEND_PID=$(lsof -ti:$BACKEND_PORT 2>/dev/null)

if [ ! -z "$FRONTEND_PID" ]; then
    echo "⚠️  发现前端服务已在运行 (PID: $FRONTEND_PID)，正在终止..."
    kill -9 $FRONTEND_PID
    sleep 1
fi

if [ ! -z "$BACKEND_PID" ]; then
    echo "⚠️  发现后端服务已在运行 (PID: $BACKEND_PID)，正在终止..."
    kill -9 $BACKEND_PID
    sleep 1
fi

# 启动后端服务
echo "🔧 启动后端服务 (端口: $BACKEND_PORT)..."
cd backend

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
if [ "$QUICK_MODE" = false ]; then
    echo "📦 安装后端依赖..."
    pip install -r requirements.txt >/dev/null 2>&1
fi

# 启动后端服务 (后台运行)
echo "🚀 启动后端服务..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > ../backend.log 2>&1 &
BACKEND_PROCESS_PID=$!

cd ..

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
for i in {1..10}; do
    if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ 后端服务启动超时"
        echo "📋 后端日志:"
        tail -n 10 backend.log 2>/dev/null || echo "无法读取后端日志"
        kill $BACKEND_PROCESS_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# 启动前端服务
echo "🌐 启动前端服务 (端口: $FRONTEND_PORT)..."

# 检查并安装前端依赖
if [ "$QUICK_MODE" = false ] && [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端服务，显示输出以便调试
echo "🚀 启动前端服务..."
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PROCESS_PID=$!

# 等待前端服务启动，并检查是否成功
echo "⏳ 等待前端服务启动..."
for i in {1..15}; do
    if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
        echo "✅ 前端服务启动成功"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "❌ 前端服务启动超时"
        echo "📋 前端日志:"
        tail -n 10 frontend.log 2>/dev/null || echo "无法读取前端日志"
        # 清理后端进程
        kill $BACKEND_PROCESS_PID 2>/dev/null
        kill $FRONTEND_PROCESS_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

echo ""
echo "✅ 项目启动完成!"
echo "   后端服务: http://localhost:$BACKEND_PORT"
echo "   前端服务: http://localhost:$FRONTEND_PORT"
echo "   API文档: http://localhost:$BACKEND_PORT/docs"
echo ""

# 如果使用 -p 参数，直接退出不监控
if [ "$NO_MONITOR" = true ]; then
    echo "💡 服务已在后台运行"
    echo "   后端进程 PID: $BACKEND_PROCESS_PID"
    echo "   前端进程 PID: $FRONTEND_PROCESS_PID"
    echo "   使用 'kill $BACKEND_PROCESS_PID $FRONTEND_PROCESS_PID' 停止服务"
    exit 0
fi

echo "💡 按 Ctrl+C 可以停止所有服务"
echo "   后端进程 PID: $BACKEND_PROCESS_PID"
echo "   前端进程 PID: $FRONTEND_PROCESS_PID"
echo ""

# 创建一个函数来清理进程
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    
    # 停止前端服务
    if [ ! -z "$FRONTEND_PROCESS_PID" ] && kill -0 $FRONTEND_PROCESS_PID 2>/dev/null; then
        kill -TERM $FRONTEND_PROCESS_PID 2>/dev/null
        sleep 2
        if kill -0 $FRONTEND_PROCESS_PID 2>/dev/null; then
            kill -9 $FRONTEND_PROCESS_PID 2>/dev/null
        fi
        echo "   已停止前端服务"
    fi
    
    # 停止后端服务
    if [ ! -z "$BACKEND_PROCESS_PID" ] && kill -0 $BACKEND_PROCESS_PID 2>/dev/null; then
        kill -TERM $BACKEND_PROCESS_PID 2>/dev/null
        sleep 2
        if kill -0 $BACKEND_PROCESS_PID 2>/dev/null; then
            kill -9 $BACKEND_PROCESS_PID 2>/dev/null
        fi
        echo "   已停止后端服务"
    fi
    
    # 清理日志文件
    rm -f frontend.log backend.log 2>/dev/null
    
    echo "✅ 所有服务已停止"
    exit 0
}

# 捕获 Ctrl+C 信号
trap cleanup SIGINT SIGTERM

# 监控进程状态，而不是无限等待
echo "🔄 监控服务状态中... (按 Ctrl+C 停止)"
while true; do
    # 检查后端进程是否还在运行
    if ! kill -0 $BACKEND_PROCESS_PID 2>/dev/null; then
        echo "❌ 后端服务意外停止"
        cleanup
        exit 1
    fi
    
    # 检查前端进程是否还在运行
    if ! kill -0 $FRONTEND_PROCESS_PID 2>/dev/null; then
        echo "❌ 前端服务意外停止"
        cleanup
        exit 1
    fi
    
    # 每5秒检查一次
    sleep 5
done