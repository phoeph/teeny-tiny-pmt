# 项目管理工具 (PMT)

## 项目概述

项目管理工具是一个基于 Web 的项目管理系统，支持项目、任务、甘特图、数据统计等功能。系统采用前后端分离架构，使用 Docker 容器化部署。

### 技术栈

**前端**
- Vue 2 + 原生 HTML/CSS/JavaScript
- 甘特图、图表可视化组件
- 现代化 UI 设计

**后端**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- MySQL 8.0 数据库
- Alembic 数据库迁移

**部署**
- Docker + Docker Compose
- Nginx 反向代理
- 自动重启和健康检查

## 系统要求

### 硬件要求
- CPU: 2 核心或以上
- 内存: 4GB RAM 或以上
- 磁盘: 20GB 可用空间

### 软件要求

**通用**
- Docker 20.10+ 
- Docker Compose 2.0+
- Git

**Windows**
- Windows 10/11 或 Windows Server 2019+
- PowerShell 5.1+

**Linux**
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- systemd 支持

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd pmt
```

### 2. 配置环境变量

复制环境变量模板并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置项（详见 [CONFIGURATION.md](./CONFIGURATION.md)）。

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 访问系统

- 前端: http://localhost
- API 文档: http://localhost/api/docs
- 健康检查: http://localhost/health

### 5. 默认账号

首次部署后，使用以下账号登录：

- 用户名: admin
- 密码: admin123

**重要：请立即修改默认密码！**

## 目录结构

```
pmt/
├── backend/              # 后端代码
│   ├── app/             # FastAPI 应用
│   ├── alembic/         # 数据库迁移
│   ├── docker/          # Docker 配置
│   ├── scripts/         # 工具脚本
│   └── tests/           # 测试文件
├── assets/              # 前端资源
├── public/              # 静态文件
├── scripts/             # 部署脚本
│   ├── linux/          # Linux 脚本
│   └── windows/        # Windows 脚本
├── docs/                # 文档
├── docker-compose.yml   # Docker 编排配置
├── nginx.conf           # Nginx 配置
└── .env                 # 环境变量（需创建）
```

## 主要功能

- **项目管理**: 创建、编辑、删除项目
- **任务管理**: 任务分配、状态跟踪、优先级管理
- **甘特图**: 可视化项目时间线和任务依赖
- **数据统计**: 项目进度、工作量统计、报表生成
- **附件管理**: 上传、下载项目相关文件
- **标签系统**: 可配置的级联标签树
- **操作日志**: 完整的操作审计记录

## 文档导航

- [部署指南](./DEPLOYMENT.md) - 详细的部署步骤
- [配置说明](./CONFIGURATION.md) - 所有配置项说明
- [更新指南](./UPDATE.md) - 系统更新和维护
- [故障排查](./TROUBLESHOOTING.md) - 常见问题解决
- [备份恢复](./BACKUP.md) - 数据备份和恢复
- [安全配置](./SECURITY.md) - 安全最佳实践

## 支持

如有问题，请查看 [故障排查文档](./TROUBLESHOOTING.md) 或联系技术支持。

## 许可证

[根据项目实际情况填写]
