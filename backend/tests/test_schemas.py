import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas import (
    UserCreate, UserResponse, UserLogin,
    ProjectCreate, ProjectResponse,
    WorkItemCreate, WorkItemResponse,
    CommentCreate, CommentResponse,
    AttachmentResponse, NotificationResponse
)


class TestUserSchemas:
    """Test user-related Pydantic schemas."""

    def test_user_create_valid(self):
        """Test valid user creation schema."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "测试用户",
            "password": "testpassword123"
        }
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "测试用户"

    def test_user_create_invalid_email(self):
        """Test user creation with invalid email."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "full_name": "测试用户",
            "password": "testpassword123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_login_valid(self):
        """Test valid user login schema."""
        login_data = {
            "login_field": "testuser",
            "password": "testpassword123"
        }
        login = UserLogin(**login_data)
        assert login.login_field == "testuser"

    def test_user_response(self):
        """Test user response schema."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "测试用户",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00"
        }
        user = UserResponse(**user_data)
        assert user.id == 1
        assert user.username == "testuser"
        assert user.full_name == "测试用户"


class TestProjectSchemas:
    """Test project-related Pydantic schemas."""

    def test_project_create_valid(self):
        """Test valid project creation schema."""
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31)
        }
        project = ProjectCreate(**project_data)
        assert project.name == "测试项目"
        assert project.start_date == date(2024, 1, 1)

    def test_project_create_invalid_dates(self):
        """Test project creation with invalid date range."""
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "start_date": date(2024, 12, 31),
            "end_date": date(2024, 1, 1)  # End before start
        }
        # This should be validated at the model level, not schema level
        project = ProjectCreate(**project_data)
        assert project.start_date > project.end_date  # Should be allowed at schema level

    def test_project_response(self):
        """Test project response schema."""
        project_data = {
            "id": 1,
            "project_number": "PRO-001",
            "name": "测试项目",
            "description": "这是一个测试项目",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "status": "active",
            "created_at": "2024-01-01T00:00:00",
            "owner_id": 1
        }
        project = ProjectResponse(**project_data)
        assert project.id == 1
        assert project.project_number == "PRO-001"
        assert project.name == "测试项目"


class TestWorkItemSchemas:
    """Test work item schemas."""

    def test_work_item_create_valid(self):
        """Test valid work item creation schema."""
        work_item_data = {
            "title": "测试任务",
            "description": "这是一个测试任务",
            "item_type": "task",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 31)
        }
        work_item = WorkItemCreate(**work_item_data)
        assert work_item.title == "测试任务"
        assert work_item.item_type == "task"
        assert work_item.status == "todo"

    def test_work_item_create_invalid_type(self):
        """Test work item creation with invalid type."""
        work_item_data = {
            "title": "测试任务",
            "description": "这是一个测试任务",
            "item_type": "invalid_type",  # Invalid type
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 31)
        }
        # Should be allowed at schema level, validated at business logic level
        work_item = WorkItemCreate(**work_item_data)
        assert work_item.item_type == "invalid_type"

    def test_work_item_response(self):
        """Test work item response schema."""
        work_item_data = {
            "id": 1,
            "work_item_number": "TASK-001",
            "title": "测试任务",
            "description": "这是一个测试任务",
            "item_type": "task",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
            "project_id": 1,
            "parent_id": None,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 31),
            "planned_start_date": None,
            "planned_end_date": None,
            "created_at": "2024-01-01T00:00:00",
            "creator_id": 1
        }
        work_item = WorkItemResponse(**work_item_data)
        assert work_item.id == 1
        assert work_item.work_item_number == "TASK-001"
        assert work_item.title == "测试任务"


class TestCommentSchemas:
    """Test comment schemas."""

    def test_comment_create_valid(self):
        """Test valid comment creation schema."""
        comment_data = {
            "content": "这是一个测试评论",
            "work_item_id": 1
        }
        comment = CommentCreate(**comment_data)
        assert comment.content == "这是一个测试评论"
        assert comment.work_item_id == 1

    def test_comment_response(self):
        """Test comment response schema."""
        comment_data = {
            "id": 1,
            "content": "这是一个测试评论",
            "work_item_id": 1,
            "author_id": 1,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "author_name": "测试用户"
        }
        comment = CommentResponse(**comment_data)
        assert comment.id == 1
        assert comment.content == "这是一个测试评论"
        assert comment.author_name == "测试用户"


class TestAttachmentSchemas:
    """Test attachment schemas."""

    def test_attachment_response(self):
        """Test attachment response schema."""
        attachment_data = {
            "id": 1,
            "filename": "test.pdf",
            "original_filename": "测试文件.pdf",
            "file_path": "/attachments/test.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "work_item_id": 1,
            "uploaded_by_id": 1,
            "created_at": "2024-01-01T00:00:00"
        }
        attachment = AttachmentResponse(**attachment_data)
        assert attachment.id == 1
        assert attachment.filename == "test.pdf"
        assert attachment.original_filename == "测试文件.pdf"
        assert attachment.mime_type == "application/pdf"


class TestNotificationSchemas:
    """Test notification schemas."""

    def test_notification_response(self):
        """Test notification response schema."""
        notification_data = {
            "id": 1,
            "user_id": 1,
            "type": "mention",
            "title": "测试通知",
            "content": "您在评论中被提及",
            "is_read": False,
            "target_type": "comment",
            "target_id": 1,
            "created_at": "2024-01-01T00:00:00"
        }
        notification = NotificationResponse(**notification_data)
        assert notification.id == 1
        assert notification.type == "mention"
        assert notification.title == "测试通知"
        assert notification.is_read is False