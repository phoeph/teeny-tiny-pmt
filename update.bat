@echo off
REM 项目更新脚本 - Windows 版本
REM 用于更新 Docker 容器化的项目管理系统

echo ======================================================
echo 项目管理系统 - 更新脚本 (Windows)
echo ======================================================
echo.

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)

REM 检查 docker-compose 是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [错误] docker-compose 未安装
    pause
    exit /b 1
)

REM 1. 备份数据库
echo [步骤 1] 备份数据库...
if not exist backups mkdir backups
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=backups\mysql_backup_%TIMESTAMP%.sql

docker ps | findstr pmt-mysql >nul 2>&1
if not errorlevel 1 (
    docker exec pmt-mysql mysqldump -u root -p%MYSQL_ROOT_PASSWORD% pmt > %BACKUP_FILE% 2>nul
    if exist %BACKUP_FILE% (
        echo [成功] 数据库备份完成: %BACKUP_FILE%
    ) else (
        echo [警告] 数据库备份失败，继续更新...
    )
) else (
    echo [警告] MySQL 容器未运行，跳过备份
)

REM 2. 拉取最新代码
echo.
echo [步骤 2] 拉取最新代码...
if exist .git (
    git pull origin main 2>nul || git pull origin master 2>nul || (
        echo [警告] Git 拉取失败，使用本地代码
    )
    for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set CURRENT_COMMIT=%%i
    echo [成功] 当前版本: %CURRENT_COMMIT%
) else (
    echo [警告] 非 Git 仓库，跳过代码拉取
    set CURRENT_COMMIT=unknown
)

REM 3. 拉取最新镜像
echo.
echo [步骤 3] 拉取最新 Docker 镜像...
docker-compose pull 2>nul || (
    echo [警告] 镜像拉取失败，使用本地镜像
)

REM 4. 重新构建镜像
echo.
echo [步骤 4] 重新构建应用镜像...
docker-compose build --no-cache backend
if errorlevel 1 (
    echo [错误] 镜像构建失败
    pause
    exit /b 1
)
echo [成功] 镜像构建完成

REM 5. 停止旧容器
echo.
echo [步骤 5] 停止旧容器...
docker-compose down
echo [成功] 旧容器已停止

REM 6. 启动新容器
echo.
echo [步骤 6] 启动新容器...
docker-compose up -d
echo [成功] 新容器已启动

REM 7. 等待服务就绪
echo.
echo [步骤 7] 等待服务就绪...
timeout /t 10 /nobreak >nul

REM 检查容器状态
echo.
echo [检查] 容器状态...
docker-compose ps

REM 8. 记录更新日志
echo.
echo [步骤 8] 记录更新日志...
echo %date% %time% - Updated to commit: %CURRENT_COMMIT% >> update.log
echo [成功] 更新日志已记录

REM 完成
echo.
echo ======================================================
echo [成功] 更新成功完成！
echo ======================================================
echo.
echo 查看日志: docker-compose logs -f
echo 查看状态: docker-compose ps
echo 访问应用: http://localhost
echo.
pause
