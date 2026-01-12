#!/bin/bash
# 项目更新脚本
# 用于更新 Docker 容器化的项目管理系统

set -e  # 遇到错误立即退出

echo "======================================================"
echo "项目管理系统 - 更新脚本"
echo "======================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose 未安装${NC}"
    exit 1
fi

# 1. 备份数据库
echo -e "${YELLOW}📦 步骤 1: 备份数据库...${NC}"
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mysql_backup_$TIMESTAMP.sql"

# 备份 MySQL 数据库
if docker ps | grep -q pmt-mysql; then
    docker exec pmt-mysql mysqldump -u root -p"${MYSQL_ROOT_PASSWORD:-changeme}" pmt > "$BACKUP_FILE" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  数据库备份失败（可能是容器未运行），继续更新...${NC}"
    }
    if [ -f "$BACKUP_FILE" ]; then
        echo -e "${GREEN}✅ 数据库备份完成: $BACKUP_FILE${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  MySQL 容器未运行，跳过备份${NC}"
fi

# 2. 拉取最新代码
echo -e "\n${YELLOW}📥 步骤 2: 拉取最新代码...${NC}"
if [ -d ".git" ]; then
    git pull origin main || git pull origin master || {
        echo -e "${YELLOW}⚠️  Git 拉取失败，使用本地代码${NC}"
    }
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    echo -e "${GREEN}✅ 当前版本: $CURRENT_COMMIT${NC}"
else
    echo -e "${YELLOW}⚠️  非 Git 仓库，跳过代码拉取${NC}"
    CURRENT_COMMIT="unknown"
fi

# 3. 拉取最新镜像
echo -e "\n${YELLOW}🐳 步骤 3: 拉取最新 Docker 镜像...${NC}"
docker-compose pull || {
    echo -e "${YELLOW}⚠️  镜像拉取失败，使用本地镜像${NC}"
}

# 4. 重新构建镜像（如果需要）
echo -e "\n${YELLOW}🔨 步骤 4: 重新构建应用镜像...${NC}"
docker-compose build --no-cache backend || {
    echo -e "${RED}❌ 镜像构建失败${NC}"
    exit 1
}
echo -e "${GREEN}✅ 镜像构建完成${NC}"

# 5. 停止旧容器
echo -e "\n${YELLOW}🛑 步骤 5: 停止旧容器...${NC}"
docker-compose down
echo -e "${GREEN}✅ 旧容器已停止${NC}"

# 6. 启动新容器
echo -e "\n${YELLOW}🚀 步骤 6: 启动新容器...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ 新容器已启动${NC}"

# 7. 等待服务就绪
echo -e "\n${YELLOW}⏳ 步骤 7: 等待服务就绪...${NC}"
sleep 10

# 检查容器状态
echo -e "\n${YELLOW}🔍 检查容器状态...${NC}"
docker-compose ps

# 检查健康状态
if docker ps | grep -q "pmt-backend.*healthy"; then
    echo -e "${GREEN}✅ 后端服务健康${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务可能未就绪，请检查日志${NC}"
fi

if docker ps | grep -q "pmt-mysql.*healthy"; then
    echo -e "${GREEN}✅ 数据库服务健康${NC}"
else
    echo -e "${YELLOW}⚠️  数据库服务可能未就绪，请检查日志${NC}"
fi

# 8. 记录更新日志
echo -e "\n${YELLOW}📝 步骤 8: 记录更新日志...${NC}"
LOG_FILE="./update.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Updated to commit: $CURRENT_COMMIT" >> "$LOG_FILE"
echo -e "${GREEN}✅ 更新日志已记录${NC}"

# 完成
echo ""
echo "======================================================"
echo -e "${GREEN}🎉 更新成功完成！${NC}"
echo "======================================================"
echo ""
echo "📊 查看日志: docker-compose logs -f"
echo "🔍 查看状态: docker-compose ps"
echo "🌐 访问应用: http://localhost"
echo ""
