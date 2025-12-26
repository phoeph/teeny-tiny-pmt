from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import OperationLog, OperationType, EntityType


class OperationLogService:
    async def log_operation(
        self,
        session: AsyncSession,
        user_id: int,
        username: str,
        operation_type: OperationType,
        entity_type: EntityType,
        entity_id: int,
        operation_content: str,
        result_status: str = "success",
        failure_reason: Optional[str] = None,
        field_name: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> OperationLog:
        log = OperationLog(
            user_id=user_id,
            username=username,
            operation_type=operation_type.value,
            entity_type=entity_type.value,
            entity_id=entity_id,
            operation_content=operation_content,
            result_status=result_status,
            failure_reason=failure_reason,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value
        )
        session.add(log)
        await session.flush()
        await session.refresh(log)
        return log

    # 字段名中英文映射
    FIELD_NAME_MAP = {
        'title': '标题',
        'name': '名称',
        'description': '描述',
        'status': '状态',
        'priority': '优先级',
        'assignee': '负责人',
        'assignee_prefix': '负责人',
        'assignee_email': '负责人邮箱',
        'planned_start_date': '计划开始日期',
        'planned_end_date': '计划结束日期',
        'actual_hours': '实际工时',
        'estimated_hours': '预估工时',
        'completed_at': '完成时间',
        'owner_id': '所有者',
        'creator_id': '创建者',
        'start_date': '开始日期',
        'end_date': '结束日期',
        'content': '内容',
        'comment': '评论'
    }

    async def log_field_change(
        self,
        session: AsyncSession,
        user_id: int,
        username: str,
        entity_type: EntityType,
        entity_id: int,
        field_name: str,
        old_value: Optional[str],
        new_value: Optional[str],
        operation_type: OperationType
    ) -> OperationLog:
        # 将字段名翻译成中文
        field_name_cn = self.FIELD_NAME_MAP.get(field_name, field_name)
        operation_content = f"将 {field_name_cn} 从 '{old_value or '(空)'}' 修改为 '{new_value or '(空)'}'"
        return await self.log_operation(
            session=session,
            user_id=user_id,
            username=username,
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            operation_content=operation_content,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value
        )

    async def get_operation_logs(
        self,
        session: AsyncSession,
        entity_type: EntityType,
        entity_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        offset = (page - 1) * page_size
        
        count_stmt = select(func.count()).select_from(OperationLog).where(
            OperationLog.entity_type == entity_type.value,
            OperationLog.entity_id == entity_id
        )
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        logs_stmt = select(OperationLog).where(
            OperationLog.entity_type == entity_type.value,
            OperationLog.entity_id == entity_id
        ).order_by(OperationLog.created_at.desc()).offset(offset).limit(page_size)
        
        logs_result = await session.execute(logs_stmt)
        logs = list(logs_result.scalars().all())
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": logs
        }

    async def get_recent_logs(
        self,
        session: AsyncSession,
        limit: int = 50
    ) -> List[OperationLog]:
        """获取最近的操作日志"""
        stmt = select(OperationLog).order_by(
            OperationLog.created_at.desc()
        ).limit(limit)
        
        result = await session.execute(stmt)
        return list(result.scalars().all())


operation_log_service = OperationLogService()