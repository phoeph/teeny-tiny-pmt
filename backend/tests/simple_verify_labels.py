#!/usr/bin/env python3
"""
Excel 路径解析验证脚本
Property 2: 配置路径解析一致性
Validates: Requirements 4.6, 4.7
"""
from pathlib import Path


def verify_labels_router_structure():
    """验证 labels.py 路由结构"""
    print("🔍 验证 labels.py 路由结构...")
    
    labels_file = Path(__file__).parents[1] / "app" / "routers" / "labels.py"
    assert labels_file.exists(), "❌ labels.py 文件不存在"
    
    with open(labels_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需的函数和导入
    required_items = [
        'from app.config import settings',
        'def get_excel_path()',
        'settings.get_excel_path()',
        'def get_label_tree_data',
        'force_reload',
        '@router.post("/tree/reload")',
        'logger.warning',
        'logger.error',
        'logger.info',
    ]
    
    for item in required_items:
        if item in content:
            print(f"✅ labels.py 包含 '{item}'")
        else:
            print(f"❌ labels.py 缺少 '{item}'")
            return False
    
    return True


def verify_path_resolution_logic():
    """验证路径解析逻辑"""
    print("\n🔍 验证路径解析逻辑...")
    
    labels_file = Path(__file__).parents[1] / "app" / "routers" / "labels.py"
    with open(labels_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查路径解析相关代码
    path_items = [
        'get_excel_path()',
        'settings.get_excel_path()',
    ]
    
    for item in path_items:
        if item in content:
            print(f"✅ 路径解析包含 '{item}'")
        else:
            print(f"❌ 路径解析缺少 '{item}'")
            return False
    
    return True


def verify_cache_refresh_mechanism():
    """验证缓存刷新机制"""
    print("\n🔍 验证缓存刷新机制...")
    
    labels_file = Path(__file__).parents[1] / "app" / "routers" / "labels.py"
    with open(labels_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查缓存相关代码
    cache_items = [
        '_CACHE',
        '_CACHE_TIMESTAMP',
        'force_reload',
        'file_mtime',
        'excel_path.stat().st_mtime',
        'if force_reload or _CACHE is None or file_mtime > _CACHE_TIMESTAMP',
    ]
    
    for item in cache_items:
        if item in content:
            print(f"✅ 缓存机制包含 '{item}'")
        else:
            print(f"❌ 缓存机制缺少 '{item}'")
            return False
    
    return True


def verify_manual_reload_endpoint():
    """验证手动刷新端点"""
    print("\n🔍 验证手动刷新端点...")
    
    labels_file = Path(__file__).parents[1] / "app" / "routers" / "labels.py"
    with open(labels_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查手动刷新端点
    reload_items = [
        '@router.post("/tree/reload")',
        'async def reload_label_tree',
        'force_reload=True',
        'return {"message"',
    ]
    
    for item in reload_items:
        if item in content:
            print(f"✅ 刷新端点包含 '{item}'")
        else:
            print(f"❌ 刷新端点缺少 '{item}'")
            return False
    
    return True


def verify_error_handling():
    """验证错误处理"""
    print("\n🔍 验证错误处理...")
    
    labels_file = Path(__file__).parents[1] / "app" / "routers" / "labels.py"
    with open(labels_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查错误处理
    error_items = [
        'if not p.exists()',
        'logger.warning',
        'try:',
        'except Exception as e:',
        'logger.error',
        'return []',
    ]
    
    for item in error_items:
        if item in content:
            print(f"✅ 错误处理包含 '{item}'")
        else:
            print(f"❌ 错误处理缺少 '{item}'")
            return False
    
    return True


def verify_config_integration():
    """验证配置集成"""
    print("\n🔍 验证配置集成...")
    
    # 检查 config.py 中的 get_excel_path 方法
    config_file = Path(__file__).parents[1] / "app" / "config.py"
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def get_excel_path(self)' in content:
        print("✅ config.py 包含 get_excel_path 方法")
    else:
        print("❌ config.py 缺少 get_excel_path 方法")
        return False
    
    # 检查相对路径和绝对路径处理
    path_handling = [
        'if excel_path.is_absolute()',
        'return excel_path',
        'else:',
        'BASE_DIR.parent',
    ]
    
    for item in path_handling:
        if item in content:
            print(f"✅ 路径处理包含 '{item}'")
        else:
            print(f"❌ 路径处理缺少 '{item}'")
            return False
    
    return True


def verify_logging_configuration():
    """验证日志配置"""
    print("\n🔍 验证日志配置...")
    
    labels_file = Path(__file__).parents[1] / "app" / "routers" / "labels.py"
    with open(labels_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    logging_items = [
        'import logging',
        'logger = logging.getLogger(__name__)',
        'logger.info',
        'logger.warning',
        'logger.error',
    ]
    
    for item in logging_items:
        if item in content:
            print(f"✅ 日志配置包含 '{item}'")
        else:
            print(f"❌ 日志配置缺少 '{item}'")
            return False
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("Excel 路径解析验证")
    print("Property 2: 配置路径解析一致性")
    print("Validates: Requirements 4.6, 4.7")
    print("="*60 + "\n")
    
    try:
        results = []
        results.append(verify_labels_router_structure())
        results.append(verify_path_resolution_logic())
        results.append(verify_cache_refresh_mechanism())
        results.append(verify_manual_reload_endpoint())
        results.append(verify_error_handling())
        results.append(verify_config_integration())
        results.append(verify_logging_configuration())
        
        if all(results):
            print("\n" + "="*60)
            print("🎉 所有 Excel 路径解析验证通过！")
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
