"""
简单测试来隔离问题
"""
import asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app


async def test_simple():
    """简单测试"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 登录
        login_response = await client.post(
            "/api/auth/login",
            json={"login_field": "张三", "password": "123"}
        )
        print(f"登录响应: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.text}")
            return
        
        token_data = login_response.json()
        token = token_data["access_token"]
        print(f"获取token: {token[:20]}...")
        
        # 创建项目
        project_data = {
            "name": "简单测试项目",
            "description": "用于简单测试的项目"
        }
        
        create_response = await client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"创建项目响应: {create_response.status_code}")
        if create_response.status_code != 200:
            print(f"创建项目失败: {create_response.text}")
            return
        
        created_project = create_response.json()
        project_id = created_project["id"]
        print(f"创建的项目ID: {project_id}")
        
        # 获取项目
        get_response = await client.get(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"获取项目响应: {get_response.status_code}")
        if get_response.status_code != 200:
            print(f"获取项目失败: {get_response.text}")
        else:
            project_data = get_response.json()
            print(f"获取的项目: {project_data['name']}, ID: {project_data['id']}")


if __name__ == "__main__":
    asyncio.run(test_simple())