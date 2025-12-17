#!/bin/bash

# 项目一键启动脚本
# 作者: Assistant
# 日期: 2025-12-17

echo "🚀 开始启动项目管理系统..."

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查是否已有进程在运行
 FRONTEND_PORT=8080
 BACKEND_PORT=8000

 FRONTEND_PID=$(lsof -ti:$FRONTEND_PORT)
 BACKEND_PID=$(lsof -ti:$BACKEND_PORT)

 if [ ! -z "$FRONTEND_PID" ]; then
     echo "⚠️  发现前端服务已在运行 (PID: $FRONTEND_PID)，正在终止..."
     kill -9 $FRONTEND_PID
 fi

 if [ ! -z "$BACKEND_PID" ]; then
     echo "⚠️  发现后端服务已在运行 (PID: $BACKEND_PID)，正在终止..."
     kill -9 $BACKEND_PID
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
echo "📦 安装后端依赖..."
pip install -r requirements.txt >/dev/null 2>&1

# 启动后端服务 (后台运行)
python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PROCESS_PID=$!

cd ..

# 等待后端服务启动
sleep 3

# 启动前端服务
echo "🌐 启动前端服务 (端口: $FRONTEND_PORT)..."
npm run dev >/dev/null 2>&1 &

echo ""
echo "✅ 项目启动完成!"
echo "   后端服务: http://localhost:$BACKEND_PORT"
echo "   前端服务: http://localhost:$FRONTEND_PORT"
echo "   API文档: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "💡 按 Ctrl+C 可以停止所有服务"
echo ""

# 等待任意进程结束
wait $BACKEND_PROCESS_PID