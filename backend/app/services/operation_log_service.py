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
        operation_content = f"将 {field_name} 从 '{old_value or '(空)'}' 修改为 '{new_value or '(空)'}'"
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


operation_log_service = OperationLogService()