#!/usr/bin/env python3
"""
集成测试：容器重启数据持久性
验证容器重启后数据不丢失
"""

import subprocess
import time
import sys
import json

def run_command(cmd):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"

def test_database_persistence():
    """测试数据库数据持久性"""
    print("测试 1: 数据库数据持久性...")
    
    # 1. 创建测试数据
    print("步骤 1: 创建测试数据...")
    test_sql = """
    CREATE TABLE IF NOT EXISTS test_persistence (
        id INT PRIMARY KEY AUTO_INCREMENT,
        test_data VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO test_persistence (test_data) VALUES ('test_value_123');
    """
    
    success, stdout, stderr = run_command(
        f'docker-compose exec -T mysql mysql -u${{MYSQL_USER}} -p${{MYSQL_PASSWORD}} ${{MYSQL_DATABASE}} -e "{test_sql}"'
    )
    
    if not success:
        print(f"❌ 失败: 无法创建测试数据")
        print(f"错误: {stderr}")
        return False
    
    print("✅ 测试数据已创建")
    
    # 2. 重启 MySQL 容器
    print("\n步骤 2: 重启 MySQL 容器...")
    success, stdout, stderr = run_command("docker-compose restart mysql")
    
    if not success:
        print(f"❌ 失败: 无法重启容器")
        return False
    
    # 等待容器启动
    print("等待容器启动...")
    time.sleep(15)
    
    # 3. 验证数据是否存在
    print("\n步骤 3: 验证数据...")
    success, stdout, stderr = run_command(
        'docker-compose exec -T mysql mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT * FROM test_persistence;"'
    )
    
    if not success:
        print(f"❌ 失败: 无法查询数据")
        print(f"错误: {stderr}")
        return False
    
    if 'test_value_123' not in stdout:
        print(f"❌ 失败: 数据丢失")
        print(f"查询结果: {stdout}")
        return False
    
    # 4. 清理测试数据
    print("\n步骤 4: 清理测试数据...")
    run_command(
        'docker-compose exec -T mysql mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "DROP TABLE IF EXISTS test_persistence;"'
    )
    
    print("✅ 通过: 数据库数据持久化正常")
    return True

def test_volume_persistence():
    """测试数据卷持久性"""
    print("\n测试 2: 数据卷持久性...")
    
    # 1. 创建测试文件
    print("步骤 1: 创建测试文件...")
    test_content = "test_persistence_file_content_123"
    
    success, stdout, stderr = run_command(
        f'docker run --rm -v pmt_attachments:/data alpine sh -c "echo {test_content} > /data/test_file.txt"'
    )
    
    if not success:
        print(f"❌ 失败: 无法创建测试文件")
        return False
    
    print("✅ 测试文件已创建")
    
    # 2. 重启后端容器
    print("\n步骤 2: 重启后端容器...")
    success, stdout, stderr = run_command("docker-compose restart backend")
    
    if not success:
        print(f"❌ 失败: 无法重启容器")
        return False
    
    # 等待容器启动
    print("等待容器启动...")
    time.sleep(10)
    
    # 3. 验证文件是否存在
    print("\n步骤 3: 验证文件...")
    success, stdout, stderr = run_command(
        'docker run --rm -v pmt_attachments:/data alpine cat /data/test_file.txt'
    )
    
    if not success:
        print(f"❌ 失败: 无法读取文件")
        return False
    
    if test_content not in stdout:
        print(f"❌ 失败: 文件内容丢失")
        print(f"文件内容: {stdout}")
        return False
    
    # 4. 清理测试文件
    print("\n步骤 4: 清理测试文件...")
    run_command(
        'docker run --rm -v pmt_attachments:/data alpine rm /data/test_file.txt'
    )
    
    print("✅ 通过: 数据卷持久化正常")
    return True

def test_restart_policy():
    """测试重启策略"""
    print("\n测试 3: 重启策略配置...")
    
    success, stdout, stderr = run_command("docker inspect pmt-backend --format '{{.HostConfig.RestartPolicy.Name}}'")
    
    if not success:
        print(f"❌ 失败: 无法获取重启策略")
        return False
    
    restart_policy = stdout.strip()
    
    if restart_policy != "unless-stopped":
        print(f"❌ 失败: 重启策略不正确，当前为: {restart_policy}")
        return False
    
    print(f"✅ 通过: 重启策略配置正确 ({restart_policy})")
    return True

def main():
    """运行所有测试"""
    print("=" * 60)
    print("容器重启数据持久性集成测试")
    print("=" * 60)
    print("\n警告: 此测试会重启容器，可能影响正在运行的服务")
    print("建议在测试环境中运行")
    print()
    
    tests = [
        test_database_persistence,
        test_volume_persistence,
        test_restart_policy,
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
        print("1. 数据卷是否正确配置")
        print("2. 重启策略是否正确设置")
        print("3. 查看容器日志: docker-compose logs")
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过！数据持久化正常！")
        sys.exit(0)

if __name__ == "__main__":
    main()
