#!/bin/bash

# Git 提交并推送脚本
# 使用方法: ./git-push.sh "提交信息"

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否提供了提交信息
if [ -z "$1" ]; then
    echo -e "${RED}❌ 错误: 请提供提交信息${NC}"
    echo -e "${YELLOW}使用方法: ./git-push.sh \"你的提交信息\"${NC}"
    exit 1
fi

COMMIT_MESSAGE="$1"

echo -e "${BLUE}🚀 开始 Git 提交流程...${NC}"
echo ""

# 1. 显示当前状态
echo -e "${BLUE}📋 检查当前状态...${NC}"
git status
echo ""

# 2. 添加所有更改
echo -e "${BLUE}➕ 添加所有更改...${NC}"
git add -A
echo -e "${GREEN}✅ 文件已添加${NC}"
echo ""

# 3. 显示将要提交的文件
echo -e "${BLUE}📝 将要提交的文件:${NC}"
git status --short
echo ""

# 4. 确认提交
read -p "$(echo -e ${YELLOW}确认提交这些更改? [y/N]: ${NC})" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 取消提交${NC}"
    exit 1
fi

# 5. 提交
echo -e "${BLUE}💾 提交更改...${NC}"
git commit -m "$COMMIT_MESSAGE"
echo -e "${GREEN}✅ 提交成功${NC}"
echo ""

# 6. 推送到远程
echo -e "${BLUE}📤 推送到 GitHub...${NC}"
BRANCH=$(git branch --show-current)
echo -e "${YELLOW}当前分支: $BRANCH${NC}"

git push origin "$BRANCH"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 推送成功!${NC}"
    echo -e "${GREEN}🎉 所有更改已提交并推送到 GitHub${NC}"
    
    # 显示最后一次提交信息
    echo ""
    echo -e "${BLUE}📊 最新提交信息:${NC}"
    git log -1 --pretty=format:"%h - %an, %ar : %s" --color
    echo ""
else
    echo ""
    echo -e "${RED}❌ 推送失败${NC}"
    echo -e "${YELLOW}💡 提示: 请检查网络连接或远程仓库权限${NC}"
    exit 1
fi
