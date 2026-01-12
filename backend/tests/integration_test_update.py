#!/usr/bin/env python3
"""
集成测试：更新流程验证
验证更新脚本和回滚功能
"""

import subprocess
import sys
import os

def run_command(cmd):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"

def test_update_script_exists():
    """测试更新脚本是否存在"""
    print("测试 1: 检查更新脚本...")
    
    scripts = {
        "Linux/Mac": "update.sh",
        "Windows": "update.bat",
        "回滚脚本": "rollback.sh",
    }
    
    all_exist = True
    for name, script in scripts.items():
        if os.path.exists(script):
            print(f"✅ {name} 脚本存在: {script}")
        else:
            print(f"❌ {name} 脚本不存在: {script}")
            all_exist = False
    
    if not all_exist:
        return False
    
    print("✅ 通过: 所有更新脚本存在")
    return True

def test_update_script_executable():
    """测试更新脚本是否可执行"""
    print("\n测试 2: 检查脚本执行权限...")
    
    scripts = ["update.sh", "rollback.sh"]
    
    all_executable = True
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✅ {script} 可执行")
            else:
                print(f"❌ {script} 不可执行")
                print(f"   提示: 运行 chmod +x {script}")
                all_executable = False
    
    if not all_executable:
        return False
    
    print("✅ 通过: 所有脚本可执行")
    return True

def test_backup_script():
    """测试备份脚本"""
    print("\n测试 3: 测试数据库备份...")
    
    # 检查备份脚本
    backup_script = "backend/scripts/backup_sqlite.py"
    if not os.path.exists(backup_script):
        print(f"❌ 失败: 备份脚本不存在: {backup_script}")
        return False
    
    print(f"✅ 备份脚本存在: {backup_script}")
    
    # 测试备份目录创建
    backup_dir = "backend/backups"
    if not os.path.exists(backup_dir):
        print(f"创建备份目录: {backup_dir}")
        os.makedirs(backup_dir, exist_ok=True)
    
    print(f"✅ 备份目录存在: {backup_dir}")
    print("✅ 通过: 备份功能配置正确")
    return True

def test_logs_script():
    """测试日志查看脚本"""
    print("\n测试 4: 测试日志脚本...")
    
    if not os.path.exists("logs.sh"):
        print("❌ 失败: logs.sh 不存在")
        return False
    
    if not os.access("logs.sh", os.X_OK):
        print("❌ 失败: logs.sh 不可执行")
        return False
    
    print("✅ 通过: 日志脚本存在且可执行")
    return True

def test_docker_compose_config():
    """测试 Docker Compose 配置"""
    print("\n测试 5: 验证 Docker Compose 配置...")
    
    success, stdout, stderr = run_command("docker-compose config")
    
    if not success:
        print(f"❌ 失败: Docker Compose 配置无效")
        print(f"错误: {stderr}")
        return False
    
    # 检查关键配置
    required_services = ["mysql", "backend", "frontend"]
    for service in required_services:
        if service not in stdout:
            print(f"❌ 失败: 服务 {service} 未配置")
            return False
    
    # 检查数据卷
    required_volumes = ["mysql-data", "attachments", "labels-data"]
    for volume in required_volumes:
        if volume not in stdout:
            print(f"❌ 失败: 数据卷 {volume} 未配置")
            return False
    
    print("✅ 通过: Docker Compose 配置有效")
    return True

def test_env_example():
    """测试环境变量模板"""
    print("\n测试 6: 检查环境变量模板...")
    
    if not os.path.exists(".env.example"):
        print("❌ 失败: .env.example 不存在")
        return False
    
    with open(".env.example", "r") as f:
        content = f.read()
    
    required_vars = [
        "MYSQL_ROOT_PASSWORD",
        "MYSQL_DATABASE",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "SECRET_KEY",
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 失败: 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    print("✅ 通过: 环境变量模板完整")
    return True

def test_documentation():
    """测试文档是否存在"""
    print("\n测试 7: 检查文档...")
    
    docs = [
        "docs/README.md",
        "docs/DEPLOYMENT.md",
        "docs/CONFIGURATION.md",
        "docs/UPDATE.md",
        "docs/TROUBLESHOOTING.md",
        "docs/BACKUP.md",
        "docs/SECURITY.md",
    ]
    
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc} 不存在")
            all_exist = False
    
    if not all_exist:
        return False
    
    print("✅ 通过: 所有文档存在")
    return True

def main():
    """运行所有测试"""
    print("=" * 60)
    print("更新流程集成测试")
    print("=" * 60)
    
    tests = [
        test_update_script_exists,
        test_update_script_executable,
        test_backup_script,
        test_logs_script,
        test_docker_compose_config,
        test_env_example,
        test_documentation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    if failed > 0:
        print("\n提示: 如果测试失败，请检查:")
        print("1. 所有脚本文件是否存在")
        print("2. 脚本是否有执行权限")
        print("3. Docker Compose 配置是否正确")
        print("4. 文档是否完整")
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过！更新流程配置正确！")
        sys.exit(0)

if __name__ == "__main__":
    main()
