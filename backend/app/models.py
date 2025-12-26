from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey, 
    Text, UniqueConstraint, CheckConstraint, Index, MetaData
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

# 使用自定义命名约定
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email_prefix = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), nullable=True)
    full_name = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    phone = Column(String(30), nullable=True)
    avatar_key = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    assigned_work_items = relationship("WorkItem", back_populates="assignee", foreign_keys="WorkItem.assignee_id")
    created_work_items = relationship("WorkItem", foreign_keys="WorkItem.creator_id")
    authored_comments = relationship("Comment", back_populates="author")
    received_notifications = relationship("Notification", back_populates="user")
    mentioned_in = relationship("Mention", back_populates="mentioned_user")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # PRO-xxxx
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="active", nullable=False)  # active, archived
    archived = Column(Boolean, default=False, nullable=False)
    label_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 约束
    __table_args__ = (
        CheckConstraint("status IN ('active', 'archived')", name="valid_project_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high')", name="valid_project_priority"),
        Index("idx_project_owner", "owner_id"),
        Index("idx_project_status", "status"),
        Index("idx_project_deleted", "deleted_at"),
    )
    
    # 关系
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    creator = relationship("User", foreign_keys=[creator_id])
    work_items = relationship("WorkItem", back_populates="project")
    non_dev_works = relationship("ProjectNonDevWork", back_populates="project")


class WorkItem(Base):
    __tablename__ = "work_items"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # JOB-xxxx or TASK-xxxx
    kind = Column(String(10), nullable=False)  # JOB or TASK
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("work_items.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="todo", nullable=False)  # todo, doing, done
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high
    label_path = Column(String(500), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    actual_hours = Column(Float, nullable=True)  # 实际工时（小时）
    estimated_hours = Column(Float, nullable=True)  # 预估工时（小时）
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 约束
    __table_args__ = (
        CheckConstraint("kind IN ('JOB', 'TASK')", name="valid_work_item_kind"),
        CheckConstraint("status IN ('todo', 'doing', 'blocked', 'done', 'cancelled', 'deleted')", name="valid_work_item_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high')", name="valid_work_item_priority"),
        # 当kind=TASK时，parent_id必须非空；当kind=JOB时，parent_id必须为空
        CheckConstraint(
            "(kind = 'TASK' AND parent_id IS NOT NULL) OR (kind = 'JOB' AND parent_id IS NULL)",
            name="valid_task_parent_constraint"
        ),
        Index("idx_work_item_project", "project_id"),
        Index("idx_work_item_parent", "parent_id"),
        Index("idx_work_item_assignee", "assignee_id"),
        Index("idx_work_item_status", "status"),
        Index("idx_work_item_deleted", "deleted_at"),
    )
    
    # 关系
    project = relationship("Project", back_populates="work_items")
    assignee = relationship("User", back_populates="assigned_work_items", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[creator_id])
    parent = relationship("WorkItem", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("WorkItem", back_populates="parent")


class ProjectNonDevWork(Base):
    """周报非开发工作说明和工作计划"""
    __tablename__ = "project_non_dev_works"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    report_period_start = Column(Date, nullable=False)  # 周报开始日期
    report_period_end = Column(Date, nullable=False)    # 周报结束日期
    work_type = Column(String(50), nullable=False, default="other_work")  # 工作类型：other_work, next_week_plan
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 约束
    __table_args__ = (
        Index("idx_non_dev_work_project", "project_id"),
        Index("idx_non_dev_work_period", "project_id", "report_period_start", "report_period_end"),
        Index("idx_non_dev_work_creator", "creator_id"),
        Index("idx_non_dev_work_deleted", "deleted_at"),
        Index("idx_non_dev_work_type", "work_type"),  # 新增类型索引
    )
    
    # 关系
    project = relationship("Project", back_populates="non_dev_works")
    creator = relationship("User", foreign_keys=[creator_id])


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)  # project, work_item
    entity_id = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 约束
    __table_args__ = (
        CheckConstraint("entity_type IN ('project', 'work_item')", name="valid_comment_entity_type"),
        Index("idx_comment_entity", "entity_type", "entity_id"),
        Index("idx_comment_author", "author_id"),
        Index("idx_comment_deleted", "deleted_at"),
    )
    
    # 关系
    author = relationship("User", back_populates="authored_comments")
    attachments = relationship("Attachment", back_populates="comment")
    mentions = relationship("Mention", back_populates="comment")


class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    file_path = Column(String(500), nullable=False)  # 相对路径
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # 字节
    mime_type = Column(String(100), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 约束
    __table_args__ = (
        Index("idx_attachment_comment", "comment_id"),
        Index("idx_attachment_uploaded_by", "uploaded_by_id"),
    )
    
    # 关系
    comment = relationship("Comment", back_populates="attachments")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])


class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    mentioned_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    anchor = Column(String(100), nullable=False)  # 定位锚点
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 约束
    __table_args__ = (
        Index("idx_mention_comment", "comment_id"),
        Index("idx_mention_user", "mentioned_user_id"),
        UniqueConstraint("comment_id", "mentioned_user_id", name="unique_mention_per_comment_user"),
    )
    
    # 关系
    comment = relationship("Comment", back_populates="mentions")
    mentioned_user = relationship("User", back_populates="mentioned_in")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # mention, comment, etc.
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    target_type = Column(String(50), nullable=False)  # comment, work_item, etc.
    target_id = Column(Integer, nullable=False)
    anchor = Column(String(100), nullable=True)  # 定位链接
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # 约束
    __table_args__ = (
        Index("idx_notification_user", "user_id"),
        Index("idx_notification_read", "is_read"),
        Index("idx_notification_created", "created_at"),
    )
    
    # 关系
    user = relationship("User", back_populates="received_notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)
    old_value = Column(String(200), nullable=True)
    new_value = Column(String(200), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_action", "action"),
    )


class Sequence(Base):
    __tablename__ = "sequences"
    
    prefix = Column(String(10), primary_key=True)  # PRO, JOB, TASK
    current_value = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 约束
    __table_args__ = (
        CheckConstraint("prefix IN ('PRO', 'JOB', 'TASK')", name="valid_sequence_prefix"),
    )


class Watch(Base):
    __tablename__ = "watches"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)
    entity_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("entity_type IN ('project', 'work_item')", name="valid_watch_entity_type"),
        UniqueConstraint("entity_type", "entity_id", "user_id", name="unique_watch_per_user_entity"),
        Index("idx_watch_entity", "entity_type", "entity_id"),
        Index("idx_watch_user", "user_id"),
    )

    user = relationship("User")


def get_active_user_query():
    """获取活跃用户的基础查询条件"""
    return User.is_active == True


def get_active_project_query():
    """获取活跃项目的基础查询条件"""
    return Project.deleted_at.is_(None)


def get_active_work_item_query():
    """获取活跃工作项的基础查询条件"""
    return WorkItem.deleted_at.is_(None)


def get_active_comment_query():
    """获取活跃评论的基础查询条件"""
    return Comment.deleted_at.is_(None)


class OperationType(str, Enum):
    CREATE_PROJECT = "create_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    ADD_MEMBER = "add_member"
    REMOVE_MEMBER = "remove_member"
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    MOVE_TASK = "move_task"
    ASSIGN_TASK = "assign_task"
    CHANGE_TASK_STATUS = "change_task_status"
    CREATE_JOB = "create_job"
    UPDATE_JOB = "update_job"
    DELETE_JOB = "delete_job"
    CHANGE_JOB_STATUS = "change_job_status"
    ADD_COMMENT = "add_comment"
    UPDATE_COMMENT = "update_comment"
    DELETE_COMMENT = "delete_comment"
    START_WATCHING = "start_watching"
    STOP_WATCHING = "stop_watching"


class EntityType(str, Enum):
    PROJECT = "project"
    WORK_ITEM = "work_item"
    JOB = "job"
    COMMENT = "comment"


class OperationLog(Base):
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(100), nullable=False)
    operation_type = Column(String(50), nullable=False)
    entity_type = Column(String(20), nullable=False)
    entity_id = Column(Integer, nullable=False)
    operation_content = Column(Text, nullable=False)
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    result_status = Column(String(20), nullable=False)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint("entity_type IN ('project', 'work_item', 'job', 'comment')", name="valid_operation_log_entity_type"),
        CheckConstraint("result_status IN ('success', 'failure')", name="valid_operation_log_result_status"),
        Index("idx_operation_logs_entity", "entity_type", "entity_id"),
        Index("idx_operation_logs_user", "user_id"),
        Index("idx_operation_logs_created", "created_at"),
    )
    
    user = relationship("User", foreign_keys=[user_id])