#!/bin/bash
# 项目回滚脚本
# 用于回滚到上一个版本

set -e  # 遇到错误立即退出

echo "======================================================"
echo "项目管理系统 - 回滚脚本"
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

# 确认回滚操作
echo -e "${YELLOW}⚠️  警告: 此操作将回滚到上一个版本${NC}"
read -p "确认继续? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "回滚已取消"
    exit 0
fi

# 1. 回滚代码
echo -e "\n${YELLOW}📥 步骤 1: 回滚代码...${NC}"
if [ -d ".git" ]; then
    # 获取当前提交
    CURRENT_COMMIT=$(git rev-parse HEAD)
    echo "当前版本: $(git rev-parse --short HEAD)"
    
    # 回滚到上一个提交
    git checkout HEAD~1 || {
        echo -e "${RED}❌ 代码回滚失败${NC}"
        exit 1
    }
    
    ROLLBACK_COMMIT=$(git rev-parse --short HEAD)
    echo -e "${GREEN}✅ 已回滚到版本: $ROLLBACK_COMMIT${NC}"
else
    echo -e "${YELLOW}⚠️  非 Git 仓库，跳过代码回滚${NC}"
    ROLLBACK_COMMIT="unknown"
fi

# 2. 重新构建镜像
echo -e "\n${YELLOW}🔨 步骤 2: 重新构建镜像...${NC}"
docker-compose build --no-cache backend || {
    echo -e "${RED}❌ 镜像构建失败${NC}"
    # 尝试恢复代码
    if [ -d ".git" ] && [ ! -z "$CURRENT_COMMIT" ]; then
        git checkout "$CURRENT_COMMIT"
    fi
    exit 1
}
echo -e "${GREEN}✅ 镜像构建完成${NC}"

# 3. 停止当前容器
echo -e "\n${YELLOW}🛑 步骤 3: 停止当前容器...${NC}"
docker-compose down
echo -e "${GREEN}✅ 容器已停止${NC}"

# 4. 启动回滚版本的容器
echo -e "\n${YELLOW}🚀 步骤 4: 启动回滚版本...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ 容器已启动${NC}"

# 5. 等待服务就绪
echo -e "\n${YELLOW}⏳ 步骤 5: 等待服务就绪...${NC}"
sleep 10

# 检查容器状态
echo -e "\n${YELLOW}🔍 检查容器状态...${NC}"
docker-compose ps

# 6. 可选：恢复数据库备份
echo -e "\n${YELLOW}💾 数据库恢复（可选）${NC}"
echo "如需恢复数据库备份，请运行:"
echo "  docker exec -i pmt-mysql mysql -u root -p\$MYSQL_ROOT_PASSWORD pmt < backups/mysql_backup_YYYYMMDD_HHMMSS.sql"
echo ""

# 7. 记录回滚日志
echo -e "${YELLOW}📝 记录回滚日志...${NC}"
LOG_FILE="./update.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Rolled back to commit: $ROLLBACK_COMMIT" >> "$LOG_FILE"
echo -e "${GREEN}✅ 回滚日志已记录${NC}"

# 完成
echo ""
echo "======================================================"
echo -e "${GREEN}🎉 回滚成功完成！${NC}"
echo "======================================================"
echo ""
echo "📊 查看日志: docker-compose logs -f"
echo "🔍 查看状态: docker-compose ps"
echo "🌐 访问应用: http://localhost"
echo ""
