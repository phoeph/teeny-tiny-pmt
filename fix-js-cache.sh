#!/bin/bash

echo "======================================"
echo "修复 JS 文件缓存问题"
echo "======================================"

# 生成版本号（使用时间戳）
VERSION=$(date +%s)
echo "版本号: $VERSION"

# 查找所有 HTML 文件并添加版本参数
echo ""
echo "正在更新 HTML 文件中的 JS 引用..."

# 更新 api-config.js 引用
find . -maxdepth 1 -name "*.html" -exec sed -i.bak "s|assets/api-config\.js\">|assets/api-config.js?v=$VERSION\">|g" {} \;
find . -maxdepth 1 -name "*.html" -exec sed -i.bak "s|assets/api-config\.js\?v=[0-9]*\">|assets/api-config.js?v=$VERSION\">|g" {} \;

# 更新 header-user-menu.js 引用
find . -maxdepth 1 -name "*.html" -exec sed -i.bak "s|assets/header-user-menu\.js\">|assets/header-user-menu.js?v=$VERSION\">|g" {} \;
find . -maxdepth 1 -name "*.html" -exec sed -i.bak "s|assets/header-user-menu\.js\?v=[0-9]*\">|assets/header-user-menu.js?v=$VERSION\">|g" {} \;

# 更新 left-sidebar.js 引用
find . -maxdepth 1 -name "*.html" -exec sed -i.bak "s|assets/left-sidebar\.js\">|assets/left-sidebar.js?v=$VERSION\">|g" {} \;
find . -maxdepth 1 -name "*.html" -exec sed -i.bak "s|assets/left-sidebar\.js\?v=[0-9]*\">|assets/left-sidebar.js?v=$VERSION\">|g" {} \;

# 删除备份文件
find . -maxdepth 1 -name "*.html.bak" -delete

echo "✓ HTML 文件更新完成"

# 重启前端容器
echo ""
echo "正在重启前端容器..."
docker-compose -f docker-compose.external-mysql.yml restart frontend

echo ""
echo "======================================"
echo "✓ 修复完成！"
echo "======================================"
echo ""
echo "请在浏览器中按 Ctrl + Shift + R 强制刷新页面"
echo ""
