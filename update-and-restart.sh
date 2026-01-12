#!/bin/bash

# 一键更新并重启服务
# 这个脚本会从 GitHub 拉取最新代码并重启服务

set -e

echo "======================================================"
echo "从 GitHub 拉取最新代码并重启服务"
echo "======================================================"

echo ""
echo "[1/5] 停止当前服务..."
docker-compose -f docker-compose.external-mysql.yml down 2>/dev/null || echo "服务已停止"

echo ""
echo "[2/5] 从 GitHub 拉取最新代码..."
git pull origin main

echo ""
echo "[3/5] 检查网络..."
if ! docker network ls | grep -q pmt_pmt-network; then
    echo "创建网络 pmt_pmt-network..."
    docker network create pmt_pmt-network
fi

# 确保 MySQL 在网络中
docker network connect pmt_pmt-network mysql-server 2>/dev/null || echo "✅ MySQL 已在网络中"

echo ""
echo "[4/5] 启动服务..."
docker-compose -f docker-compose.external-mysql.yml up -d --build

echo ""
echo "[5/5] 等待服务启动..."
sleep 15

echo ""
echo "======================================================"
echo "服务状态："
echo "======================================================"
docker-compose -f docker-compose.external-mysql.yml ps

echo ""
echo "======================================================"
echo "后端日志（最后 30 行）："
echo "======================================================"
docker logs pmt-backend --tail 30

echo ""
echo "======================================================"
echo "测试 API："
echo "======================================================"
curl -s http://localhost/api/health && echo "" && echo "✅ API 正常" || echo "❌ API 异常"

echo ""
echo "======================================================"
echo "检查网络中的容器："
echo "======================================================"
docker network inspect pmt_pmt-network --format '容器列表: {{range .Containers}}{{.Name}} {{end}}'

echo ""
echo "完成！访问 http://124.220.35.110 测试登录"
