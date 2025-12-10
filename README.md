# Teeny Tiny PMT

一个极简的项目管理工具，集成看板与甘特图视图，支持 JOB/TASK 创建、编辑、排期、负责人与优先级管理，并有基础的评论与附件能力。前后端可独立运行：前端为纯静态页面，后端为 FastAPI。

## 功能概览
- 看板视图：按状态列展示 JOB 与脱离父任务的 TASK，支持拖拽变更状态
- 甘特视图：年/月/日三层时间轴，支持日/月两种模式
- JOB/TASK 管理：创建、编辑、删除，支持描述、负责人、状态、时间、优先级（Low/Medium/High）
- 负责人选择：下拉提示与本地缓存，支持邮箱前缀映射
- 级联校验：TASK 时间范围受父 JOB 约束，父范围调整可自动夹紧子范围
- 评论与附件：在详情页加载评论模块与附件列表（需要后端）

## 技术栈
- 前端：原生 HTML/CSS/JS（`index.html`、`project.html`、`job.html`、`task.html` 等）
- 后端：FastAPI（`backend/app/main.py`），SQLite 数据库，Alembic 迁移
- 开发服务：`serve` 本地静态资源服务

## 快速开始
- 克隆仓库
```bash
git clone https://github.com/phoeph/teeny-tiny-pmt.git
cd teeny-tiny-pmt
```
- 启动前端（静态）
```bash
npm install
npm run dev  # 默认 http://localhost:8080
```
- 启动后端（可选）
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

前端默认访问 `http://localhost:8000/api` 作为接口地址，若后端未启动，页面仍可在 demo 数据或本地缓存下工作，但部分编辑能力将受限。

## 主要页面
- `index.html`：首页与导航
- `project.html`：项目总览（看板 + 甘特视图），支持创建/编辑 JOB/TASK、优先级设置（默认 Medium）、负责人选择
- `job.html`：单个 JOB 详情，展示子任务、评论与附件
- `task.html`：单个 TASK 详情（如开启）

## 常用脚本
- `npm run dev`：本地静态服务（前端）
- `npm start`：同上
- `npm run build`：拷贝静态资源到 `dist/`
- 后端：参考上文 uvicorn 命令启动

## 配置与部署
- `.gitignore`：忽略点开头目录与任意 `scripts` 目录、`node_modules/` 与 `dist/`
- `cnb-config.yaml`：示例构建配置，已指向仓库 `phoeph/teeny-tiny-pmt`
- `backend/.env`：后端环境配置（示例文件），包含基础安全与数据库配置

## 许可
- MIT

## 贡献
- 欢迎提交 Issue 与 PR

如果这个项目对你有帮助，请 Star 支持！
