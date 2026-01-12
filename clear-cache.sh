#!/bin/bash

# 清理缓存脚本 - 解决部署后显示旧版本问题
# 使用方法: ./clear-cache.sh

set -e

echo "🧹 开始清理缓存..."

# 1. 清理 Docker 容器缓存
echo "🐳 重启 Docker 容器..."
if command -v docker &> /dev/null; then
    # 停止并删除现有容器
    docker stop $(docker ps -q --filter "ancestor=nginx") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "ancestor=nginx") 2>/dev/null || true
    
    # 删除旧镜像
    docker rmi $(docker images -q --filter "reference=*nginx*") 2>/dev/null || true
    
    echo "✅ Docker 容器已清理"
else
    echo "⚠️  Docker 未安装，跳过容器清理"
fi

# 2. 重新构建并启动
echo "🔨 重新构建项目..."
if [ -f "Dockerfile" ]; then
    docker build -t pmt-frontend .
    docker run -d -p 80:80 --name pmt-app pmt-frontend
    echo "✅ 项目已重新部署"
else
    echo "⚠️  未找到 Dockerfile"
fi

# 3. 提供清理浏览器缓存的说明
echo ""
echo "🌐 浏览器缓存清理说明:"
echo "   Chrome/Edge: Ctrl+Shift+R 或 F12 -> Network -> Disable cache"
echo "   Firefox: Ctrl+Shift+R 或 F12 -> Network -> 齿轮图标 -> Disable cache"
echo "   Safari: Cmd+Option+R"
echo ""
echo "🔗 访问地址: http://your-server-ip"
echo ""
echo "✅ 缓存清理完成！"