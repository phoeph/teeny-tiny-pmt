-- MySQL 初始化脚本
-- 此脚本在 MySQL 容器首次启动时自动执行

-- 设置字符集为 utf8mb4，支持完整的 Unicode 字符（包括 emoji）
ALTER DATABASE pmt CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- 确保用户权限正确
-- 注意：用户已经通过环境变量创建，这里只是确认权限
GRANT ALL PRIVILEGES ON pmt.* TO 'pmt_user'@'%';
FLUSH PRIVILEGES;

-- 设置时区为 UTC（可根据需要调整）
SET GLOBAL time_zone = '+00:00';

-- 优化 MySQL 配置（可选）
-- 设置最大连接数
SET GLOBAL max_connections = 200;

-- 设置查询缓存（MySQL 8.0 已移除查询缓存，此行仅作为注释说明）
-- MySQL 8.0+ 不再支持查询缓存，依赖更好的优化器

-- 记录初始化完成
SELECT 'MySQL initialization completed successfully' AS status;
