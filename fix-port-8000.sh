#!/bin/bash

echo "======================================"
echo "统一使用 8000 端口配置"
echo "======================================"

echo ""
echo "[1/4] 停止当前服务..."
docker-compose -f docker-compose.external-mysql.yml down

echo ""
echo "[2/4] 检查端口占用..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  警告：8000 端口已被占用"
    echo "正在查看占用进程..."
    lsof -i :8000
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

echo ""
echo "[3/4] 重新构建并启动服务..."
docker-compose -f docker-compose.external-mysql.yml up -d --build

echo ""
echo "[4/4] 等待服务启动..."
sleep 10

echo ""
echo "======================================"
echo "✓ 配置完成！"
echo "======================================"
echo ""
echo "前端访问地址: http://124.220.35.110:8000"
echo "API 地址: http://124.220.35.110:8000/api"
echo ""
echo "查看服务状态:"
echo "  docker-compose -f docker-compose.external-mysql.yml ps"
echo ""
echo "查看日志:"
echo "  docker logs pmt-frontend"
echo "  docker logs pmt-backend"
echo ""
