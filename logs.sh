#!/bin/bash
# 日志查看脚本
# 用于查看 Docker 容器日志

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "======================================================"
echo "项目管理系统 - 日志查看"
echo "======================================================"
echo ""

# 显示菜单
echo "请选择要查看的日志:"
echo "  1) 所有服务"
echo "  2) MySQL 数据库"
echo "  3) 后端应用"
echo "  4) 前端 Nginx"
echo "  5) 实时跟踪所有日志"
echo "  6) 搜索日志"
echo "  0) 退出"
echo ""
read -p "请输入选项 (0-6): " choice

case $choice in
    1)
        echo -e "\n${BLUE}📊 查看所有服务日志（最近 100 行）${NC}"
        docker-compose logs --tail=100
        ;;
    2)
        echo -e "\n${BLUE}📊 查看 MySQL 日志（最近 100 行）${NC}"
        docker-compose logs --tail=100 mysql
        ;;
    3)
        echo -e "\n${BLUE}📊 查看后端应用日志（最近 100 行）${NC}"
        docker-compose logs --tail=100 backend
        ;;
    4)
        echo -e "\n${BLUE}📊 查看前端 Nginx 日志（最近 100 行）${NC}"
        docker-compose logs --tail=100 frontend
        ;;
    5)
        echo -e "\n${BLUE}📊 实时跟踪所有日志（Ctrl+C 退出）${NC}"
        docker-compose logs -f
        ;;
    6)
        read -p "请输入搜索关键词: " keyword
        echo -e "\n${BLUE}🔍 搜索包含 '$keyword' 的日志${NC}"
        docker-compose logs | grep -i "$keyword" --color=always
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}⚠️  无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "======================================================"
echo "其他有用的命令:"
echo "  docker-compose logs -f [service]  # 实时跟踪特定服务"
echo "  docker-compose logs --tail=N      # 查看最近 N 行"
echo "  docker-compose logs --since=10m   # 查看最近 10 分钟"
echo "======================================================"
