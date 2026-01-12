#!/bin/bash
# 推送项目到新的 GitHub 仓库

set -e

echo "======================================================"
echo "推送项目到新 GitHub 仓库"
echo "======================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 新仓库地址
NEW_REPO="https://github.com/phoeph/teeny-tiny-pmt-prod.git"

echo -e "${BLUE}目标仓库: $NEW_REPO${NC}"
echo ""

# ============================================
# 步骤 1: 检查 Git 状态
# ============================================
echo -e "${YELLOW}[步骤 1/6] 检查 Git 状态...${NC}"
echo ""

# 显示当前状态
git status

echo ""
read -p "是否继续？(y/n) [y]: " CONTINUE
CONTINUE=${CONTINUE:-y}

if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
    echo "已取消"
    exit 0
fi

echo ""

# ============================================
# 步骤 2: 添加所有更改
# ============================================
echo -e "${YELLOW}[步骤 2/6] 添加所有更改...${NC}"
echo ""

# 添加所有文件
git add .

echo -e "${GREEN}✅ 文件已添加${NC}"
echo ""

# ============================================
# 步骤 3: 提交更改
# ============================================
echo -e "${YELLOW}[步骤 3/6] 提交更改...${NC}"
echo ""

# 询问提交信息
read -p "请输入提交信息 [feat: 完成 Docker + MySQL 部署配置]: " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"feat: 完成 Docker + MySQL 部署配置"}

# 提交
git commit -m "$COMMIT_MSG" || echo "没有需要提交的更改"

echo -e "${GREEN}✅ 更改已提交${NC}"
echo ""

# ============================================
# 步骤 4: 添加新的远程仓库
# ============================================
echo -e "${YELLOW}[步骤 4/6] 配置远程仓库...${NC}"
echo ""

# 检查是否已有 prod 远程仓库
if git remote | grep -q "^prod$"; then
    echo "远程仓库 'prod' 已存在，正在更新..."
    git remote set-url prod "$NEW_REPO"
else
    echo "添加新的远程仓库 'prod'..."
    git remote add prod "$NEW_REPO"
fi

echo -e "${GREEN}✅ 远程仓库配置完成${NC}"
echo ""

# 显示所有远程仓库
echo "当前远程仓库："
git remote -v
echo ""

# ============================================
# 步骤 5: 推送到新仓库
# ============================================
echo -e "${YELLOW}[步骤 5/6] 推送到新仓库...${NC}"
echo ""

echo "正在推送到 $NEW_REPO ..."
echo ""

# 推送到新仓库（强制推送，因为是新仓库）
git push -u prod main --force

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 推送成功！${NC}"
else
    echo ""
    echo -e "${RED}❌ 推送失败${NC}"
    echo ""
    echo "可能的原因："
    echo "1. 没有权限访问该仓库"
    echo "2. 需要配置 GitHub 认证"
    echo "3. 仓库地址错误"
    echo ""
    echo "解决方案："
    echo "1. 确保你有该仓库的写权限"
    echo "2. 配置 GitHub Personal Access Token"
    echo "3. 或使用 SSH 方式推送"
    exit 1
fi

echo ""

# ============================================
# 步骤 6: 验证推送
# ============================================
echo -e "${YELLOW}[步骤 6/6] 验证推送...${NC}"
echo ""

echo "检查远程分支..."
git ls-remote --heads prod

echo ""
echo "======================================================"
echo -e "${GREEN}🎉 推送完成！${NC}"
echo "======================================================"
echo ""
echo "新仓库地址: $NEW_REPO"
echo ""
echo "后续操作："
echo "1. 访问 GitHub 查看新仓库"
echo "2. 如果需要，可以将 prod 设为默认远程仓库："
echo "   git remote rename origin old-origin"
echo "   git remote rename prod origin"
echo ""
echo "3. 或者保留两个远程仓库："
echo "   推送到原仓库: git push origin main"
echo "   推送到新仓库: git push prod main"
echo ""
