from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import DATABASE_URL
from .exceptions import AppException
from .database import engine
from . import models  # Import models to create tables
import bcrypt

app = FastAPI(
    title="项目管理系统",
    description="基于甘特图的项目管理系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:65300", "http://127.0.0.1:65300"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "details": {"error": str(exc)}
        }
    )


@app.on_event("startup")
async def startup():
    # 创建数据库表（使用同步引擎避免greenlet依赖）
    from sqlalchemy import create_engine as create_sync_engine
    from sqlalchemy import text
    from .config import DATABASE_URL
    sync_url = DATABASE_URL.replace("+aiosqlite", "")
    sync_engine = create_sync_engine(sync_url)
    with sync_engine.begin() as conn:
        models.Base.metadata.create_all(conn)
        # 轻量迁移：为projects添加creator_id列（若不存在），并填充默认值
        try:
            cols = conn.execute(text("PRAGMA table_info(projects)")).fetchall()
            names = {c[1] for c in cols}  # (cid, name, type, notnull, dflt_value, pk)
            if "creator_id" not in names:
                conn.execute(text("ALTER TABLE projects ADD COLUMN creator_id INTEGER"))
                conn.execute(text("UPDATE projects SET creator_id = owner_id WHERE creator_id IS NULL"))
            if "priority" not in names:
                conn.execute(text("ALTER TABLE projects ADD COLUMN priority TEXT"))
                conn.execute(text("UPDATE projects SET priority = 'medium' WHERE priority IS NULL"))
            if "label_path" not in names:
                conn.execute(text("ALTER TABLE projects ADD COLUMN label_path TEXT"))
        except Exception as e:
            # 忽略迁移错误，确保服务可启动
            pass
        # 轻量迁移：为work_items添加estimated_hours列（若不存在）
        try:
            cols_wi = conn.execute(text("PRAGMA table_info(work_items)")).fetchall()
            names_wi = {c[1] for c in cols_wi}
            if "estimated_hours" not in names_wi:
                conn.execute(text("ALTER TABLE work_items ADD COLUMN estimated_hours REAL"))
            if "label_path" not in names_wi:
                conn.execute(text("ALTER TABLE work_items ADD COLUMN label_path TEXT"))
        except Exception:
            pass
        # 轻量迁移：创建project_non_dev_works表（若不存在）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS project_non_dev_works (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    report_period_start DATE NOT NULL,
                    report_period_end DATE NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    creator_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    deleted_at DATETIME,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (creator_id) REFERENCES users(id)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_non_dev_work_project ON project_non_dev_works(project_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_non_dev_work_period ON project_non_dev_works(project_id, report_period_start, report_period_end)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_non_dev_work_creator ON project_non_dev_works(creator_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_non_dev_work_deleted ON project_non_dev_works(deleted_at)"))
        except Exception:
            pass
        
        # 轻量迁移：为project_non_dev_works添加work_type字段（若不存在）
        try:
            cols_ndw = conn.execute(text("PRAGMA table_info(project_non_dev_works)")).fetchall()
            names_ndw = {c[1] for c in cols_ndw}
            if "work_type" not in names_ndw:
                conn.execute(text("ALTER TABLE project_non_dev_works ADD COLUMN work_type VARCHAR(50) DEFAULT 'other_work'"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_non_dev_work_type ON project_non_dev_works(work_type)"))
        except Exception:
            pass
        # 轻量迁移：为users添加phone与avatar_key列（若不存在）
        try:
            cols_u = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            names_u = {c[1] for c in cols_u}
            if "phone" not in names_u:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone TEXT"))
            if "avatar_key" not in names_u:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_key TEXT"))
            if "email" not in names_u:
                conn.execute(text("ALTER TABLE users ADD COLUMN email TEXT"))
            if "full_name" not in names_u:
                conn.execute(text("ALTER TABLE users ADD COLUMN full_name TEXT"))
        except Exception:
            pass
        try:
            rows = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
            exists = rows.first() is not None
            if not exists:
                pw = bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                conn.execute(text("INSERT INTO users (username, email_prefix, password_hash, is_active, created_at) VALUES (:u, :e, :p, 1, CURRENT_TIMESTAMP)")
                             , {"u": "admin", "e": "admin", "p": pw})
            # 预置演示用户，确保前后端一致
            demo_users = [
                {"username":"demo", "email_prefix":"demo", "full_name":"呆某"},
                {"username":"zhangs123", "email_prefix":"zhangs123", "full_name":"张三"},
                {"username":"zhif1", "email_prefix":"zhif1", "full_name":"智飞"},
                {"username":"zhangxm", "email_prefix":"zhangxm", "full_name":"张项目"}
            ]
            for du in demo_users:
                try:
                    row = conn.execute(text("SELECT id FROM users WHERE username = :u"), {"u": du["username"]}).first()
                    if not row:
                        pw = bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        conn.execute(text("INSERT INTO users (username, email_prefix, password_hash, is_active, full_name, created_at) VALUES (:u, :e, :p, 1, :f, CURRENT_TIMESTAMP)"),
                                     {"u": du["username"], "e": du["email_prefix"], "p": pw, "f": du.get("full_name")})
                except Exception:
                    pass
        except Exception:
            pass


@app.get("/health")
def health():
    return {"status": "ok", "database": DATABASE_URL}


# 导入并注册路由
from .routers import auth, project, work_items, comments, notifications, attachments, users, labels, exports, non_dev_works
from .routers import watch, operation_logs
app.include_router(auth.router)
app.include_router(project.router)
app.include_router(work_items.router)
app.include_router(comments.router)
app.include_router(notifications.router)
app.include_router(attachments.router)
app.include_router(watch.router)
app.include_router(operation_logs.router)
app.include_router(users.router)
app.include_router(labels.router)
app.include_router(exports.router)
app.include_router(non_dev_works.router)
