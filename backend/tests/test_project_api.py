"""
项目API测试
"""
import pytest
from datetime import date, timedelta
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models import User, Project
from app.database import get_db
from app.services.auth_service import auth_service


@pytest.mark.asyncio
async def test_create_project():
    """测试创建项目"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 创建项目
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=30))
        }
        
        response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试项目"
        assert data["description"] == "这是一个测试项目"
        assert data["code"].startswith("PRO")
        assert data["status"] == "active"
        assert data["archived"] == False
        assert data["owner_id"] > 0


@pytest.mark.asyncio
async def test_get_project():
    """测试获取项目详情"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 先创建一个项目
        project_data = {
            "name": "获取测试项目",
            "description": "用于测试获取的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # 获取项目详情
        response = await client.get(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "获取测试项目"
        assert data["code"] == created_project["code"]


@pytest.mark.asyncio
async def test_list_projects():
    """测试获取项目列表"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 创建多个项目
        for i in range(3):
            project_data = {
                "name": f"列表测试项目{i+1}",
                "description": f"第{i+1}个测试项目"
            }
            create_response = await client.post(
                "/api/projects/",
                json=project_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            assert create_response.status_code == 200
        
        # 获取项目列表
        response = await client.get(
            "/api/projects/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["size"] == 10
        assert len(data["items"]) >= 3  # 至少包含我们创建的3个项目


@pytest.mark.asyncio
async def test_update_project():
    """测试更新项目"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 先创建一个项目
        project_data = {
            "name": "更新测试项目",
            "description": "原始描述"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # 更新项目
        update_data = {
            "name": "更新后的项目名称",
            "description": "更新后的描述"
        }
        
        response = await client.put(
            f"/api/projects/{project_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的项目名称"
        assert data["description"] == "更新后的描述"
        assert data["id"] == project_id


@pytest.mark.asyncio
async def test_archive_project():
    """测试归档项目"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 先创建一个项目
        project_data = {
            "name": "归档测试项目",
            "description": "用于测试归档的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # 归档项目
        response = await client.post(
            f"/api/projects/{project_id}/archive",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["archived"] == True
        assert data["status"] == "archived"


@pytest.mark.asyncio
async def test_unarchive_project():
    """测试取消归档项目"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 先创建一个项目并归档
        project_data = {
            "name": "取消归档测试项目",
            "description": "用于测试取消归档的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # 归档项目
        archive_response = await client.post(
            f"/api/projects/{project_id}/archive",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert archive_response.status_code == 200
        
        # 取消归档项目
        response = await client.post(
            f"/api/projects/{project_id}/unarchive",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["archived"] == False
        assert data["status"] == "active"


@pytest.mark.asyncio
async def test_soft_delete_project():
    """测试软删除项目"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 先创建一个项目
        project_data = {
            "name": "软删除测试项目",
            "description": "用于测试软删除的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # 软删除项目
        response = await client.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_at"] is not None
        
        # 验证项目不在正常列表中
        list_response = await client.get(
            "/api/projects/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        projects = list_response.json()["items"]
        project_ids = [p["id"] for p in projects]
        assert project_id not in project_ids
        
        # 验证可以通过include_deleted获取
        get_response = await client.get(
            f"/api/projects/{project_id}?include_deleted=true",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 200
        deleted_project = get_response.json()
        assert deleted_project["deleted_at"] is not None


@pytest.mark.asyncio
async def test_restore_project():
    """测试恢复软删除的项目"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 先创建一个项目并软删除
        project_data = {
            "name": "恢复测试项目",
            "description": "用于测试恢复的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # 软删除项目
        delete_response = await client.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert delete_response.status_code == 200
        
        # 恢复项目
        response = await client.post(
            f"/api/projects/{project_id}/restore",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_at"] is None
        
        # 验证项目已回到正常列表
        list_response = await client.get(
            "/api/projects/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        projects = list_response.json()["items"]
        project_ids = [p["id"] for p in projects]
        assert project_id in project_ids


@pytest.mark.asyncio
async def test_project_statistics():
    """测试项目统计"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # 先创建一个项目
        project_data = {
            "name": "统计测试项目",
            "description": "用于测试统计的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # 获取项目统计
        response = await client.get(
            f"/api/projects/{project_id}/statistics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id
        assert data["total_work_items"] >= 0
        assert data["todo_count"] >= 0
        assert data["doing_count"] >= 0
        assert data["done_count"] >= 0


@pytest.mark.asyncio
async def test_permission_check():
    """测试权限验证"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 张三登录并创建项目
        zhangsan_login = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        assert zhangsan_login.status_code == 200
        zhangsan_token = zhangsan_login.json()["access_token"]
        
        # 李四登录
        lisi_login = await client.post(
            "/api/auth/login",
            json={"login_field": "李四", "password": "123"}
        )
        assert lisi_login.status_code == 200
        lisi_token = lisi_login.json()["access_token"]
        
        # 张三创建项目
        project_data = {
            "name": "权限测试项目",
            "description": "用于测试权限的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {zhangsan_token}"}
        )
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]
        
        # 李四尝试更新张三的项目（应该失败）
        update_data = {"name": "李四尝试修改"}
        update_response = await client.put(
            f"/api/projects/{project_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {lisi_token}"}
        )
        
        assert update_response.status_code == 403
        error_data = update_response.json()
        assert "只有项目所有者可以更新项目" in str(error_data)