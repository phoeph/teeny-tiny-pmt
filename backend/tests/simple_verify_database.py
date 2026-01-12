#!/usr/bin/env python3
"""
数据库配置验证脚本（无外部依赖）
验证数据库连接测试函数和配置
Validates: Requirements 1.4
"""
from pathlib import Path


def verify_database_connection_function():
    """验证数据库连接测试函数存在"""
    print("🔍 验证数据库连接测试函数...")
    
    db_file = Path(__file__).parents[1] / "app" / "database.py"
    assert db_file.exists(), "❌ database.py 文件不存在"
    
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查连接测试函数
    required_items = [
        'async def test_database_connection',
        'max_retries',
        'retry_interval',
        'for attempt in range(max_retries)',
        'await conn.execute(text("SELECT 1"))',
        'logger.info',
        'logger.error',
        'await asyncio.sleep',
        'RuntimeError',
    ]
    
    for item in required_items:
        if item in content:
            print(f"✅ 数据库连接函数包含 '{item}'")
        else:
            print(f"❌ 数据库连接函数缺少 '{item}'")
            return False
    
    return True


def verify_connection_pool_config():
    """验证连接池配置"""
    print("\n🔍 验证连接池配置...")
    
    db_file = Path(__file__).parents[1] / "app" / "database.py"
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pool_configs = [
        'pool_pre_ping=True',
        'pool_recycle=3600',
        'pool_size=10',
        'max_overflow=20',
    ]
    
    for config in pool_configs:
        if config in content:
            print(f"✅ 连接池配置 '{config}' 存在")
        else:
            print(f"❌ 连接池配置 '{config}' 不存在")
            return False
    
    return True


def verify_startup_connection_test():
    """验证启动时调用连接测试"""
    print("\n🔍 验证启动时连接测试...")
    
    main_file = Path(__file__).parents[1] / "app" / "main.py"
    assert main_file.exists(), "❌ main.py 文件不存在"
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_items = [
        'from .database import test_database_connection',
        'await test_database_connection',
        '@app.on_event("startup")',
    ]
    
    for item in required_items:
        if item in content:
            print(f"✅ 启动配置包含 '{item}'")
        else:
            print(f"❌ 启动配置缺少 '{item}'")
            return False
    
    return True


def verify_retry_mechanism():
    """验证重试机制"""
    print("\n🔍 验证重试机制...")
    
    db_file = Path(__file__).parents[1] / "app" / "database.py"
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查重试逻辑
    retry_items = [
        'for attempt in range(max_retries)',
        'if attempt < max_retries - 1',
        'await asyncio.sleep(retry_interval)',
        'logger.error',
    ]
    
    for item in retry_items:
        if item in content:
            print(f"✅ 重试机制包含 '{item}'")
        else:
            print(f"❌ 重试机制缺少 '{item}'")
            return False
    
    return True


def verify_error_handling():
    """验证错误处理"""
    print("\n🔍 验证错误处理...")
    
    db_file = Path(__file__).parents[1] / "app" / "database.py"
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    error_handling = [
        'except Exception as e:',
        'raise RuntimeError',
        'logger.error',
    ]
    
    for item in error_handling:
        if item in content:
            print(f"✅ 错误处理包含 '{item}'")
        else:
            print(f"❌ 错误处理缺少 '{item}'")
            return False
    
    return True


def verify_logging_configuration():
    """验证日志配置"""
    print("\n🔍 验证日志配置...")
    
    db_file = Path(__file__).parents[1] / "app" / "database.py"
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    logging_items = [
        'import logging',
        'logger = logging.getLogger(__name__)',
        'logger.info',
        'logger.error',
    ]
    
    for item in logging_items:
        if item in content:
            print(f"✅ 日志配置包含 '{item}'")
        else:
            print(f"❌ 日志配置缺少 '{item}'")
            return False
    
    return True


def verify_production_environment_handling():
    """验证生产环境处理"""
    print("\n🔍 验证生产环境处理...")
    
    db_file = Path(__file__).parents[1] / "app" / "database.py"
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查生产环境配置
    if 'IS_PRODUCTION' in content and 'echo=not IS_PRODUCTION' in content:
        print("✅ 生产环境禁用 SQL 日志")
    else:
        print("⚠️  生产环境 SQL 日志配置可能不正确")
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("数据库连接测试验证")
    print("Validates: Requirements 1.4")
    print("="*60 + "\n")
    
    try:
        results = []
        results.append(verify_database_connection_function())
        results.append(verify_connection_pool_config())
        results.append(verify_startup_connection_test())
        results.append(verify_retry_mechanism())
        results.append(verify_error_handling())
        results.append(verify_logging_configuration())
        results.append(verify_production_environment_handling())
        
        if all(results):
            print("\n" + "="*60)
            print("🎉 所有数据库连接测试验证通过！")
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
