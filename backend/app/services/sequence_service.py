"""
全局编号服务 - 事务生成唯一编号（PRO/JOB/TASK）
"""
import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.models import Sequence


class SequenceService:
    """全局编号服务"""
    
    def __init__(self):
        self._lock = asyncio.Lock()
    
    async def generate_code(self, session: AsyncSession, prefix: str) -> str:
        """
        生成唯一编号
        
        Args:
            session: 数据库会话
            prefix: 编号前缀 ('PRO', 'JOB', 'TASK')
            
        Returns:
            生成的唯一编号 (如: PRO-0001, JOB-0001, TASK-0001)
            
        Raises:
            ValueError: 如果前缀无效
        """
        if prefix not in ['PRO', 'JOB', 'TASK']:
            raise ValueError(f"无效的前缀: {prefix}. 必须是 'PRO', 'JOB', 或 'TASK'")
        
        async with self._lock:
            # 获取或创建序列
            sequence = await session.get(Sequence, prefix)
            
            if not sequence:
                # 创建新的序列，起始值为0（生成编号从0001开始）
                sequence = Sequence(prefix=prefix, current_value=0)
                session.add(sequence)
                await session.flush()
            
            # 增加序列值
            sequence.current_value += 1
            
            # 生成编号，格式为: PREFIX-XXXX
            code = f"{prefix}-{sequence.current_value:04d}"
            
            # 提交事务
            await session.commit()
            
            return code
    
    async def get_next_value(self, session: AsyncSession, prefix: str) -> int:
        """
        获取下一个序列值（不增加）
        
        Args:
            session: 数据库会话
            prefix: 编号前缀
            
        Returns:
            下一个序列值
        """
        sequence = await session.get(Sequence, prefix)
        if not sequence:
            return 1  # 默认下一个值（从0001开始）
        return sequence.current_value + 1
    
    async def reset_sequence(self, session: AsyncSession, prefix: str, start_value: int = 0):
        """
        重置序列值（仅用于测试或维护）
        
        Args:
            session: 数据库会话
            prefix: 编号前缀
            start_value: 新的开始值
        """
        sequence = await session.get(Sequence, prefix)
        if sequence:
            sequence.current_value = start_value
        else:
            sequence = Sequence(prefix=prefix, current_value=start_value)
            session.add(sequence)
        
        await session.commit()


# 创建全局实例
sequence_service = SequenceService()
