import os
from pathlib import Path
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/app.db")

# 附件目录配置
ATTACHMENTS_DIR = Path(os.getenv("ATTACHMENTS_DIR", str(BASE_DIR / "attachments")))
ATTACHMENTS_DIR.mkdir(exist_ok=True)

# 支持的附件类型
ALLOWED_MIME_TYPES = {
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "text/plain": ".txt",
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
}

MAX_ATTACHMENT_SIZE = 50 * 1024 * 1024  # 50MB

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Excel 标签文件路径配置
LABELS_EXCEL_PATH = os.getenv("LABELS_EXCEL_PATH", ".docs/tech/菜单级联关系.xlsx")

# 轮询配置
NOTIFICATION_POLL_INTERVAL = 60  # 秒


class Settings(BaseSettings):
    """应用设置"""
    # 数据库配置
    database_url: str = DATABASE_URL
    
    # Excel 标签文件路径
    labels_excel_path: str = LABELS_EXCEL_PATH
    
    # 附件存储路径
    attachments_dir: Path = ATTACHMENTS_DIR
    
    # JWT 配置
    secret_key: str = SECRET_KEY
    algorithm: str = ALGORITHM
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    
    class Config:
        env_file = ".env"
    
    def validate_config(self) -> bool:
        """验证配置完整性和有效性"""
        errors = []
        
        # 检查数据库 URL
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        
        # 检查 JWT 密钥
        if self.secret_key == "your-secret-key-change-in-production":
            logger.warning("⚠️  SECRET_KEY is using default value. Please change it in production!")
            # 在开发环境允许使用默认值，但记录警告
        
        # 检查 Excel 文件路径
        excel_path = Path(self.labels_excel_path)
        if not excel_path.is_absolute():
            # 相对路径，相对于项目根目录
            excel_path = BASE_DIR.parent / self.labels_excel_path
        
        if not excel_path.exists():
            logger.warning(f"⚠️  Labels Excel file not found: {excel_path}")
            # 不阻止启动，只记录警告
        
        # 检查附件目录
        if not self.attachments_dir.exists():
            try:
                self.attachments_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created attachments directory: {self.attachments_dir}")
            except Exception as e:
                errors.append(f"Failed to create attachments directory: {e}")
        
        if errors:
            error_msg = f"Configuration errors: {', '.join(errors)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        logger.info("✅ Configuration validation passed")
        return True
    
    def get_excel_path(self) -> Path:
        """获取 Excel 文件的绝对路径"""
        excel_path = Path(self.labels_excel_path)
        
        if excel_path.is_absolute():
            return excel_path
        else:
            # 相对路径，相对于项目根目录
            return BASE_DIR.parent / self.labels_excel_path


# 创建设置实例
settings = Settings()

# 启动时验证配置
try:
    settings.validate_config()
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    # 在开发环境允许继续，生产环境应该退出
    if os.getenv("ENVIRONMENT") == "production":
        raise
