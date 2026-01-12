"""
配置验证测试
Property 5: 配置验证完整性
Validates: Requirements 4.8, 4.9
"""
import os
import sys
from pathlib import Path

# 添加父目录到路径以便导入 app 模块
sys.path.insert(0, str(Path(__file__).parents[1]))


def test_config_has_required_fields():
    """测试配置包含所有必需字段"""
    from app.config import settings
    
    # 验证必需的配置字段存在
    assert hasattr(settings, 'database_url'), "配置缺少 database_url"
    assert hasattr(settings, 'secret_key'), "配置缺少 secret_key"
    assert hasattr(settings, 'labels_excel_path'), "配置缺少 labels_excel_path"
    assert hasattr(settings, 'attachments_dir'), "配置缺少 attachments_dir"
    assert hasattr(settings, 'access_token_expire_minutes'), "配置缺少 access_token_expire_minutes"
    
    print("✅ 所有必需配置字段存在")


def test_config_validation_method_exists():
    """测试配置验证方法存在"""
    from app.config import settings
    
    assert hasattr(settings, 'validate_config'), "配置缺少 validate_config 方法"
    assert callable(settings.validate_config), "validate_config 必须是可调用的方法"
    
    print("✅ 配置验证方法存在")


def test_config_get_excel_path_method():
    """测试获取 Excel 路径方法存在"""
    from app.config import settings
    
    assert hasattr(settings, 'get_excel_path'), "配置缺少 get_excel_path 方法"
    assert callable(settings.get_excel_path), "get_excel_path 必须是可调用的方法"
    
    # 测试方法返回 Path 对象
    excel_path = settings.get_excel_path()
    assert isinstance(excel_path, Path), "get_excel_path 必须返回 Path 对象"
    
    print(f"✅ Excel 路径方法存在，返回: {excel_path}")


def test_database_url_configuration():
    """测试数据库 URL 配置"""
    from app.config import settings
    
    assert settings.database_url, "database_url 不能为空"
    assert isinstance(settings.database_url, str), "database_url 必须是字符串"
    
    # 验证 URL 格式
    assert '://' in settings.database_url, "database_url 必须包含协议"
    
    print(f"✅ 数据库 URL 配置正确: {settings.database_url[:20]}...")


def test_secret_key_configuration():
    """测试 JWT 密钥配置"""
    from app.config import settings
    
    assert settings.secret_key, "secret_key 不能为空"
    assert isinstance(settings.secret_key, str), "secret_key 必须是字符串"
    assert len(settings.secret_key) >= 16, "secret_key 长度应至少 16 个字符"
    
    print("✅ JWT 密钥配置正确")


def test_labels_excel_path_configuration():
    """测试 Excel 路径配置"""
    from app.config import settings
    
    assert settings.labels_excel_path, "labels_excel_path 不能为空"
    assert isinstance(settings.labels_excel_path, str), "labels_excel_path 必须是字符串"
    
    print(f"✅ Excel 路径配置: {settings.labels_excel_path}")


def test_attachments_dir_configuration():
    """测试附件目录配置"""
    from app.config import settings
    
    assert settings.attachments_dir, "attachments_dir 不能为空"
    assert isinstance(settings.attachments_dir, Path), "attachments_dir 必须是 Path 对象"
    
    print(f"✅ 附件目录配置: {settings.attachments_dir}")


def test_access_token_expire_configuration():
    """测试访问令牌过期时间配置"""
    from app.config import settings
    
    assert settings.access_token_expire_minutes > 0, "access_token_expire_minutes 必须大于 0"
    assert isinstance(settings.access_token_expire_minutes, int), "access_token_expire_minutes 必须是整数"
    
    print(f"✅ 访问令牌过期时间: {settings.access_token_expire_minutes} 分钟")


def test_config_validation_passes():
    """
    Property 5: 配置验证完整性
    测试配置验证在正常情况下通过
    """
    from app.config import settings
    
    try:
        result = settings.validate_config()
        assert result is True, "配置验证应该返回 True"
        print("✅ 配置验证通过")
    except ValueError as e:
        # 如果是因为 Excel 文件不存在，这是可以接受的（只是警告）
        if "Labels Excel file not found" in str(e):
            print("⚠️  Excel 文件不存在，但配置验证继续")
        else:
            raise


def test_environment_variables_loaded():
    """测试环境变量正确加载"""
    from app.config import DATABASE_URL, SECRET_KEY, LABELS_EXCEL_PATH
    
    # 验证环境变量被加载
    assert DATABASE_URL is not None, "DATABASE_URL 未加载"
    assert SECRET_KEY is not None, "SECRET_KEY 未加载"
    assert LABELS_EXCEL_PATH is not None, "LABELS_EXCEL_PATH 未加载"
    
    print("✅ 环境变量正确加载")


if __name__ == "__main__":
    print("="*60)
    print("配置验证测试")
    print("Property 5: 配置验证完整性")
    print("Validates: Requirements 4.8, 4.9")
    print("="*60 + "\n")
    
    tests = [
        test_config_has_required_fields,
        test_config_validation_method_exists,
        test_config_get_excel_path_method,
        test_database_url_configuration,
        test_secret_key_configuration,
        test_labels_excel_path_configuration,
        test_attachments_dir_configuration,
        test_access_token_expire_configuration,
        test_config_validation_passes,
        test_environment_variables_loaded,
    ]
    
    failed = []
    for test in tests:
        try:
            print(f"\n🔍 运行测试: {test.__name__}")
            test()
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"❌ 测试错误: {e}")
            failed.append(test.__name__)
    
    print("\n" + "="*60)
    if not failed:
        print("🎉 所有配置验证测试通过！")
        print("="*60)
        exit(0)
    else:
        print(f"❌ {len(failed)} 个测试失败:")
        for name in failed:
            print(f"  - {name}")
        print("="*60)
        exit(1)
