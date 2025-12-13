import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from app.main import app
from app.database import async_session
from app.models import User
from app.services.auth_service import auth_service


@pytest.mark.asyncio
async def test_create_job_and_task_with_assignee_prefix():
    async with async_session() as session:
        res_admin = await session.execute(select(User).where(User.username == 'admin'))
        admin = res_admin.scalar_one_or_none()
        if not admin:
            admin = User(username='admin', email_prefix='admin', email='admin@chinaunicom.cn', full_name='管理员', password_hash=auth_service.get_password_hash('123456'), is_active=True)
            session.add(admin)
        else:
            admin.is_active = True
        res_zs = await session.execute(select(User).where(User.username == '张三'))
        zs = res_zs.scalar_one_or_none()
        if not zs:
            zs = User(username='张三', email_prefix='zhangsan', email='zhangsan@chinaunicom.cn', full_name='张三', password_hash=auth_service.get_password_hash('123456'), is_active=True)
            session.add(zs)
        else:
            zs.is_active = True
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login = await client.post("/api/auth/login", json={"login_field": "张三", "password": "123456"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        proj = await client.post("/api/projects/", json={"name": "创建负责人测试项目"}, headers=headers)
        assert proj.status_code == 200
        project_id = proj.json()["id"]

        # 创建JOB，传入 assignee_prefix
        job = await client.post(
            "/api/work-items/",
            json={
                "kind": "JOB",
                "project_id": project_id,
                "title": "测试父任务",
                "status": "todo",
                "assignee_prefix": "zhangsan",
            },
            headers=headers,
        )
        assert job.status_code == 200
        job_id = job.json()["id"]
        assert job.json().get("assignee_id") is not None

        # 创建TASK，传入 assignee_prefix
        task = await client.post(
            "/api/work-items/",
            json={
                "kind": "TASK",
                "project_id": project_id,
                "parent_id": job_id,
                "title": "测试子任务",
                "status": "todo",
                "assignee_prefix": "zhangsan",
            },
            headers=headers,
        )
        assert task.status_code == 200
        assert task.json().get("assignee_id") is not None

