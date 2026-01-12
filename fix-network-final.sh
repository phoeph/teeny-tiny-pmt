#!/bin/bash

# 最终网络修复脚本
# 修复 docker-compose.external-mysql.yml 网络配置问题

set -e

echo "======================================================"
echo "修复 Docker 网络配置"
echo "======================================================"

echo ""
echo "[1/4] 停止现有服务..."
docker-compose -f docker-compose.external-mysql.yml down

echo ""
echo "[2/4] 验证 MySQL 容器和网络..."
if ! docker ps | grep -q mysql-server; then
    echo "❌ MySQL 容器未运行"
    exit 1
fi

if ! docker network ls | grep -q pmt_pmt-network; then
    echo "⚠️  网络 pmt_pmt-network 不存在，创建中..."
    docker network create pmt_pmt-network
fi

# 确保 MySQL 在网络中
if ! docker network inspect pmt_pmt-network | grep -q mysql-server; then
    echo "将 MySQL 加入网络..."
    docker network connect pmt_pmt-network mysql-server 2>/dev/null || echo "⚠️  MySQL 已在网络中"
fi

echo "✅ MySQL 和网络准备就绪"

echo ""
echo "[3/4] 启动服务（使用外部网络）..."
docker-compose -f docker-compose.external-mysql.yml up -d

echo ""
echo "[4/4] 等待服务启动..."
sleep 10

echo ""
echo "======================================================"
echo "检查服务状态"
echo "======================================================"
docker-compose -f docker-compose.external-mysql.yml ps

echo ""
echo "检查网络连接："
docker network inspect pmt_pmt-network --format '{{range .Containers}}{{.Name}} {{end}}'

echo ""
echo "======================================================"
echo "查看后端日志（最后 20 行）："
echo "======================================================"
docker logs pmt-backend --tail 20

echo ""
echo "======================================================"
echo "测试 API："
echo "======================================================"
sleep 5
curl -s http://localhost/api/health || echo "⚠️  API 未响应"

echo ""
echo "======================================================"
echo "✅ 修复完成！"
echo "======================================================"
echo ""
echo "如果仍有问题，请检查："
echo "1. docker logs pmt-backend"
echo "2. docker network inspect pmt_pmt-network"
echo "3. docker exec pmt-backend ping mysql-server"
