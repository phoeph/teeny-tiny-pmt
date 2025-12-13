import pytest
from datetime import date, timedelta
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_work_items_batch_update_and_constraints():
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
        proj = await client.post("/api/projects/", json={"name": "甘特批量更新测试"}, headers=headers)
        assert proj.status_code == 200
        project_id = proj.json()["id"]

        # 创建父 JOB（11/10~11/20）
        job = await client.post(
            "/api/work-items/",
            json={
                "kind": "JOB",
                "project_id": project_id,
                "title": "父任务",
                "status": "todo",
                "planned_start_date": "2025-11-10",
                "planned_end_date": "2025-11-20",
            },
            headers=headers,
        )
        assert job.status_code == 200
        job_id = job.json()["id"]

        # 创建两个子 TASK（分别 11/12~11/14 与 11/15~11/18）
        t1 = await client.post(
            "/api/work-items/",
            json={
                "kind": "TASK",
                "project_id": project_id,
                "parent_id": job_id,
                "title": "子A",
                "status": "todo",
                "planned_start_date": "2025-11-12",
                "planned_end_date": "2025-11-14",
            },
            headers=headers,
        )
        assert t1.status_code == 200
        a_id = t1.json()["id"]

        t2 = await client.post(
            "/api/work-items/",
            json={
                "kind": "TASK",
                "project_id": project_id,
                "parent_id": job_id,
                "title": "子B",
                "status": "todo",
                "planned_start_date": "2025-11-15",
                "planned_end_date": "2025-11-18",
            },
            headers=headers,
        )
        assert t2.status_code == 200
        b_id = t2.json()["id"]

        # 约束失败场景：尝试将父 JOB 收缩到 11/13~11/14（小于子任务最大跨度）
        bad = await client.patch(
            "/api/work-items/batch",
            json={"items": [{"id": job_id, "planned_start_date": "2025-11-13", "planned_end_date": "2025-11-14"}]},
            headers=headers,
        )
        assert bad.status_code in (400, 422)

        # 合法批量：将父移至 11/11~11/20，并将子任务夹紧到新窗口（这里子范围原本已在父窗口内，仍应返回成功）
        ok = await client.patch(
            "/api/work-items/batch",
            json={
                "items": [
                    {"id": job_id, "planned_start_date": "2025-11-11", "planned_end_date": "2025-11-20"},
                    {"id": a_id, "planned_start_date": "2025-11-12", "planned_end_date": "2025-11-14"},
                    {"id": b_id, "planned_start_date": "2025-11-15", "planned_end_date": "2025-11-18"},
                ]
            },
            headers=headers,
        )
        assert ok.status_code == 200
        ret = ok.json()
        assert "items" in ret and len(ret["items"]) == 3

        # 列表接口返回嵌套结构（TASK 在 JOB 内部）
        listing = await client.get(f"/api/work-items/by-project/{project_id}", headers=headers)
        assert listing.status_code == 200
        data = listing.json()
        assert "items" in data and len(data["items"]) >= 1
        parent = next((it for it in data["items"] if it.get("id") == job_id), None)
        assert parent is not None
        subs = parent.get("subtasks") or []
        assert isinstance(subs, list) and len(subs) >= 2
