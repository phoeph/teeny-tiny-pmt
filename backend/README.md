# 项目管理系统后端

基于 FastAPI 的项目管理系统后端，支持项目、任务、子任务管理，状态看板，评论系统，附件上传等功能。

## 技术栈

- **框架**: FastAPI (异步)
- **数据库**: SQLite + SQLAlchemy (异步)
- **迁移**: Alembic
- **测试**: pytest + httpx
- **认证**: JWT
- **Python版本**: 3.8+

## 项目结构

```
backend/
├── app/                    # 应用代码
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   ├── config.py          # 配置
│   ├── database.py        # 数据库连接
│   ├── schemas.py         # Pydantic 数据模型
│   ├── exceptions.py      # 自定义异常
│   ├── models/            # SQLAlchemy 数据模型 (待创建)
│   ├── routers/           # API 路由 (待创建)
│   ├── services/          # 业务逻辑 (待创建)
│   └── utils/             # 工具函数 (待创建)
├── alembic/               # 数据库迁移
│   ├── versions/          # 迁移版本文件
│   ├── env.py             # 迁移环境配置
│   └── script.py.mako     # 迁移模板
├── tests/                  # 测试文件
│   ├── conftest.py        # pytest 配置
│   ├── test_main.py       # 主应用测试
│   ├── test_database.py   # 数据库测试
│   ├── test_schemas.py    # 数据模型测试
│   └── test_exceptions.py # 异常处理测试
├── attachments/           # 附件存储目录
├── requirements.txt       # 依赖包
├── pytest.ini            # pytest 配置
├── alembic.ini           # Alembic 配置
└── README.md              # 项目说明
```

## 安装与运行

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
# 创建迁移文件
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 4. 运行应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 访问文档

- API 文档: http://localhost:8000/docs
- 备用文档: http://localhost:8000/redoc

## 测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_main.py
pytest tests/test_database.py
pytest tests/test_schemas.py
pytest tests/test_exceptions.py
```

### 运行测试并显示详细信息

```bash
pytest -v
```

### 运行测试并显示覆盖率

```bash
pytest --cov=app
```

## 数据库迁移

### 创建新的迁移

```bash
alembic revision --autogenerate -m "Description of changes"
```

### 应用迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
alembic downgrade -1
```

### 查看迁移历史

```bash
alembic history
```

## 配置

### 环境变量

- `DATABASE_URL`: 数据库连接字符串 (默认: SQLite)
- `SECRET_KEY`: JWT 密钥 (生产环境必须设置)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT 过期时间 (默认: 30分钟)

### 附件配置

- 支持文件类型: Word, Excel, PDF, TXT, PNG, JPG
- 最大文件大小: 50MB
- 存储目录: `attachments/`

## API 端点

### 健康检查

- `GET /health` - 系统健康状态
- `GET /` - API 信息

### 认证 (待实现)

- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 当前用户信息

### 项目 (待实现)

- `GET /projects` - 项目列表
- `POST /projects` - 创建项目
- `GET /projects/{id}` - 项目详情
- `PUT /projects/{id}` - 更新项目
- `DELETE /projects/{id}` - 删除项目

### 工作项 (待实现)

- `GET /work-items` - 工作项列表
- `POST /work-items` - 创建工作项
- `GET /work-items/{id}` - 工作项详情
- `PUT /work-items/{id}` - 更新工作项
- `DELETE /work-items/{id}` - 删除工作项

### 评论 (待实现)

- `GET /work-items/{id}/comments` - 评论列表
- `POST /work-items/{id}/comments` - 创建评论

### 附件 (待实现)

- `POST /work-items/{id}/attachments` - 上传附件
- `GET /attachments/{id}` - 下载附件

### 通知 (待实现)

- `GET /notifications` - 通知列表
- `PUT /notifications/{id}/read` - 标记已读

## 开发规范

### 测试驱动开发

1. 先写测试用例
2. 运行测试确认失败
3. 实现功能代码
4. 运行测试确认通过
5. 重构优化

### 代码规范

- 使用类型注解
- 遵循 PEP 8 规范
- 添加适当的错误处理
- 编写清晰的文档字符串

### 提交规范

- 使用清晰的提交信息
- 每个提交对应一个功能
- 包含测试用例

## 功能特性

### 已实现

- ✅ 基础框架搭建
- ✅ 数据库连接配置
- ✅ Pydantic 数据模型
- ✅ 统一异常处理
- ✅ 测试框架配置
- ✅ 健康检查端点

### 待实现

根据 `.docs/specs/project-management-system/tasks.md` 中的任务列表：

1. 定义数据模型与迁移 - 建立所有表结构与软删支持
2. 实现全局编号服务 - 事务生成唯一编号（PRO/JOB/TASK）
3. 实现认证与当前用户接口 - 支持中文名与邮箱前缀登录
4. 实现项目API - 列表/详情/归档/软删功能
5. 实现工作项API - 任务/子任务统一模型与状态拖拽
6. 实现评论与@解析 - 支持中文重名候选选择
7. 实现附件上传与下载 - 类型与大小校验
8. 实现工作台轮询通知 - 未读消息与定位链接
9. 实现甘特图数据接口与聚合 - 项目页统一数据源
10. 实现软删可视系统管理视图 - 只读接口
11. 实现归档只读强制 - 拦截写操作中间件
12. 完成测试覆盖与E2E - 并发/状态流转/评论@/附件
13. 实现前端登录页与路由 - 演示账号与跳转
14. 创建演示数据种子 - 两套项目与多状态任务
15. 增加planned字段与接口 - 甘特图计划时间支持
16. 实现项目列表与详情导航 - 看板与甘特图展示
17. 完成E2E演示流 - 登录到甘特图完整流程

## 注意事项

1. 开发环境使用 SQLite，生产环境建议 PostgreSQL
2. 附件文件存储在本地文件系统，生产环境建议使用云存储
3. JWT 密钥在生产环境必须设置为强随机字符串
4. 定期备份数据库和附件文件

## 联系方式

如有问题，请通过以下方式联系：

- 邮箱: [your-email@example.com]
- 项目地址: [your-project-url]