#!/bin/bash
# 腾讯云超简化部署脚本
# 适用于已有 mysql-server 容器的环境

set -e

echo "======================================================"
echo "PMT 一键部署（腾讯云版）"
echo "======================================================"
echo ""

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================
# 1. 检查 MySQL 容器
# ============================================
echo -e "${YELLOW}[1/6] 检查 MySQL 容器...${NC}"

if ! docker ps | grep -q mysql-server; then
    echo -e "${RED}❌ 未找到 mysql-server 容器${NC}"
    echo "请先启动 MySQL 容器"
    exit 1
fi

echo -e "${GREEN}✅ MySQL 容器运行中${NC}"
echo ""

# ============================================
# 2. 配置
# ============================================
echo -e "${YELLOW}[2/6] 配置参数...${NC}"

# 默认配置
MYSQL_HOST="mysql-server"
MYSQL_PORT="3306"
MYSQL_DATABASE="pmt_db"
MYSQL_USER="root"

# 询问密码
read -sp "请输入 MySQL root 密码 [123456]: " MYSQL_PASSWORD
echo ""
MYSQL_PASSWORD=${MYSQL_PASSWORD:-123456}

# 前端端口
read -p "前端端口 [80]: " FRONTEND_PORT
FRONTEND_PORT=${FRONTEND_PORT:-80}

# 检测端口是否被占用
if sudo lsof -i :${FRONTEND_PORT} &> /dev/null; then
    echo -e "${RED}⚠️  端口 ${FRONTEND_PORT} 已被占用${NC}"
    echo ""
    sudo lsof -i :${FRONTEND_PORT}
    echo ""
    read -p "是否使用其他端口？(y/n) [y]: " CHANGE_PORT
    CHANGE_PORT=${CHANGE_PORT:-y}
    
    if [ "$CHANGE_PORT" = "y" ] || [ "$CHANGE_PORT" = "Y" ]; then
        read -p "请输入新端口 [8080]: " FRONTEND_PORT
        FRONTEND_PORT=${FRONTEND_PORT:-8080}
        echo -e "${GREEN}✓ 使用端口: ${FRONTEND_PORT}${NC}"
    fi
fi

# 生成密钥
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)

# 创建 .env
cat > .env << EOF
DATABASE_URL=mysql+aiomysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}
MYSQL_HOST=${MYSQL_HOST}
MYSQL_PORT=${MYSQL_PORT}
MYSQL_DATABASE=${MYSQL_DATABASE}
MYSQL_USER=${MYSQL_USER}
MYSQL_PASSWORD=${MYSQL_PASSWORD}
SECRET_KEY=${SECRET_KEY}
LABELS_EXCEL_PATH=/data/labels/菜单级联关系.xlsx
FRONTEND_PORT=${FRONTEND_PORT}
ENVIRONMENT=production
EOF

echo -e "${GREEN}✅ 配置完成${NC}"
echo ""

# ============================================
# 3. 配置网络
# ============================================
echo -e "${YELLOW}[3/6] 配置 Docker 网络...${NC}"

# 创建网络
docker network create pmt_pmt-network 2>/dev/null || echo "网络已存在"

# 将 MySQL 加入网络
docker network connect pmt_pmt-network mysql-server 2>/dev/null || echo "MySQL 已在网络中"

echo -e "${GREEN}✅ 网络配置完成${NC}"
echo ""

# ============================================
# 4. 创建数据库
# ============================================
echo -e "${YELLOW}[4/6] 创建数据库...${NC}"

docker run --rm --network pmt_pmt-network mysql:8.0 \
    mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} \
    -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null

echo -e "${GREEN}✅ 数据库就绪${NC}"
echo ""

# ============================================
# 5. 构建和启动
# ============================================
echo -e "${YELLOW}[5/6] 构建应用...${NC}"

docker-compose -f docker-compose.external-mysql.yml build

echo -e "${GREEN}✅ 构建完成${NC}"
echo ""

echo -e "${YELLOW}启动服务...${NC}"

docker-compose -f docker-compose.external-mysql.yml up -d

echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""

# ============================================
# 6. 验证
# ============================================
echo -e "${YELLOW}[6/6] 验证部署...${NC}"

sleep 5

docker-compose -f docker-compose.external-mysql.yml ps

echo ""
echo "======================================================"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "======================================================"
echo ""
echo "访问地址: http://$(hostname -I | awk '{print $1}'):${FRONTEND_PORT}"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose -f docker-compose.external-mysql.yml logs -f"
echo "  重启: docker-compose -f docker-compose.external-mysql.yml restart"
echo "  停止: docker-compose -f docker-compose.external-mysql.yml down"
echo ""
echo "如果无法访问，请检查防火墙:"
echo "  sudo ufw allow ${FRONTEND_PORT}/tcp"
echo ""
