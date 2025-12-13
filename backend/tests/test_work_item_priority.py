import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_update_priority_single_and_batch():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 直接往数据库写入演示用户
        from sqlalchemy import select
        from app.database import async_session
        from app.models import User
        from app.services.auth_service import auth_service
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

        # 登录张三
        login = await client.post("/api/auth/login", json={"login_field": "张三", "password": "123456"})
        assert login.status_code == 200
        token = login.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # 创建项目
        proj = await client.post("/api/projects/", json={"name": "优先级测试项目"}, headers=headers)
        assert proj.status_code == 200
        project_id = proj.json()["id"]

        # 创建父 JOB
        job = await client.post(
            "/api/work-items/",
            json={
                "kind": "JOB",
                "project_id": project_id,
                "title": "优先级父任务",
                "status": "todo",
            },
            headers=headers,
        )
        assert job.status_code == 200
        job_id = job.json()["id"]

        # 创建子 TASK
        task = await client.post(
            "/api/work-items/",
            json={
                "kind": "TASK",
                "project_id": project_id,
                "parent_id": job_id,
                "title": "优先级子任务",
                "status": "todo",
            },
            headers=headers,
        )
        assert task.status_code == 200
        task_id = task.json()["id"]

        # 单项更新：将子任务优先级改为 high
        up = await client.patch(f"/api/work-items/{task_id}", json={"priority": "high"}, headers=headers)
        assert up.status_code == 200
        assert up.json().get("priority") == "high"

        # 批量更新：将父JOB优先级改为 low
        bat = await client.patch(
            "/api/work-items/batch",
            json={"items": [{"id": job_id, "priority": "low"}]},
            headers=headers,
        )
        assert bat.status_code == 200
        items = bat.json().get("items") or []
        assert any(it.get("id") == job_id and it.get("priority") == "low" for it in items)
