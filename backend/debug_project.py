"""
调试项目API问题
"""
import asyncio
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models import User, Project
from app.services.project_service import project_service
from app.services.auth_service import auth_service
from app.schemas.project import ProjectCreate


async def debug_project():
    """调试项目创建和获取"""
    async with async_session() as session:
        from sqlalchemy import select
        
        # 获取用户
        result = await session.execute(select(User).where(User.username == "张三"))
        user = result.scalar_one_or_none()
        if not user:
            print("用户张三未找到")
            return
        print(f"用户: {user.id}, {user.username}")
        
        # 创建项目
        project_data = ProjectCreate(
            name="调试项目",
            description="用于调试的项目"
        )
        
        project = await project_service.create_project(session, project_data, user.id)
        print(f"创建的项目: {project.id}, {project.name}, owner_id: {project.owner_id}")
        
        # 立即获取项目
        retrieved_project = await project_service.get_project(session, project.id)
        print(f"获取的项目: {retrieved_project}")
        
        if retrieved_project:
            print(f"获取的项目详情: {retrieved_project.id}, {retrieved_project.name}, owner_id: {retrieved_project.owner_id}")
        
        # 检查数据库中的项目
        result = await session.execute(select(Project).where(Project.id == project.id))
        db_project = result.scalar_one_or_none()
        print(f"数据库中的项目: {db_project}")
        
        if db_project:
            print(f"数据库项目详情: {db_project.id}, {db_project.name}, owner_id: {db_project.owner_id}")


if __name__ == "__main__":
    asyncio.run(debug_project())