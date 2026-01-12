#!/usr/bin/env python3
"""
配置验证简单脚本（无外部依赖）
Property 5: 配置验证完整性
Validates: Requirements 4.8, 4.9
"""
from pathlib import Path


def verify_config_file_structure():
    """验证 config.py 文件结构"""
    print("🔍 验证 config.py 文件结构...")
    
    config_file = Path(__file__).parents[1] / "app" / "config.py"
    assert config_file.exists(), "❌ config.py 文件不存在"
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需的配置项
    required_configs = [
        'DATABASE_URL',
        'SECRET_KEY',
        'LABELS_EXCEL_PATH',
        'ATTACHMENTS_DIR',
        'ACCESS_TOKEN_EXPIRE_MINUTES',
        'class Settings',
        'def validate_config',
        'def get_excel_path',
    ]
    
    for config in required_configs:
        if config in content:
            print(f"✅ 配置项 '{config}' 存在")
        else:
            print(f"❌ 配置项 '{config}' 不存在")
            return False
    
    # 检查环境变量读取
    env_vars = [
        'os.getenv("DATABASE_URL"',
        'os.getenv("SECRET_KEY"',
        'os.getenv("LABELS_EXCEL_PATH"',
        'os.getenv("ATTACHMENTS_DIR"',
        'os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"',
    ]
    
    for var in env_vars:
        if var in content:
            print(f"✅ 环境变量读取 '{var}' 存在")
        else:
            print(f"❌ 环境变量读取 '{var}' 不存在")
            return False
    
    # 检查配置验证逻辑
    validation_checks = [
        'if not self.database_url',
        'if self.secret_key ==',
        'if not excel_path.exists()',
        'logger.warning',
        'logger.error',
    ]
    
    for check in validation_checks:
        if check in content:
            print(f"✅ 验证逻辑 '{check}' 存在")
        else:
            print(f"⚠️  验证逻辑 '{check}' 可能不存在")
    
    return True


def verify_env_example_completeness():
    """验证 .env.example 包含所有必需的配置项"""
    print("\n🔍 验证 .env.example 完整性...")
    
    env_file = Path(__file__).parents[2] / ".env.example"
    assert env_file.exists(), "❌ .env.example 文件不存在"
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_vars = [
        'MYSQL_ROOT_PASSWORD',
        'MYSQL_DATABASE',
        'MYSQL_USER',
        'MYSQL_PASSWORD',
        'SECRET_KEY',
        'ACCESS_TOKEN_EXPIRE_MINUTES',
        'LABELS_EXCEL_PATH',
    ]
    
    for var in required_vars:
        if var in content:
            print(f"✅ 环境变量 '{var}' 在 .env.example 中")
        else:
            print(f"❌ 环境变量 '{var}' 不在 .env.example 中")
            return False
    
    # 检查是否有使用说明
    if '注意事项' in content or 'NOTE' in content.upper():
        print("✅ .env.example 包含使用说明")
    else:
        print("⚠️  .env.example 可能缺少使用说明")
    
    return True


def verify_database_config():
    """验证 database.py 配置"""
    print("\n🔍 验证 database.py 配置...")
    
    db_file = Path(__file__).parents[1] / "app" / "database.py"
    assert db_file.exists(), "❌ database.py 文件不存在"
    
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_configs = [
        'create_async_engine',
        'pool_pre_ping=True',
        'pool_recycle=',
        'pool_size=',
        'max_overflow=',
        'echo=not IS_PRODUCTION',
    ]
    
    for config in required_configs:
        if config in content:
            print(f"✅ 数据库配置 '{config}' 存在")
        else:
            print(f"❌ 数据库配置 '{config}' 不存在")
            return False
    
    return True


def verify_config_integration():
    """验证配置集成"""
    print("\n🔍 验证配置集成...")
    
    # 检查 config.py 是否在启动时验证配置
    config_file = Path(__file__).parents[1] / "app" / "config.py"
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'settings.validate_config()' in content:
        print("✅ 配置在启动时自动验证")
    else:
        print("⚠️  配置可能不会在启动时自动验证")
    
    # 检查是否有日志记录
    if 'logger' in content and 'logging' in content:
        print("✅ 配置包含日志记录")
    else:
        print("⚠️  配置可能缺少日志记录")
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("配置验证测试")
    print("Property 5: 配置验证完整性")
    print("Validates: Requirements 4.8, 4.9")
    print("="*60 + "\n")
    
    try:
        results = []
        results.append(verify_config_file_structure())
        results.append(verify_env_example_completeness())
        results.append(verify_database_config())
        results.append(verify_config_integration())
        
        if all(results):
            print("\n" + "="*60)
            print("🎉 所有配置验证测试通过！")
            print("="*60)
            exit(0)
        else:
            print("\n" + "="*60)
            print("❌ 部分验证失败，请检查上述错误")
            print("="*60)
            exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
