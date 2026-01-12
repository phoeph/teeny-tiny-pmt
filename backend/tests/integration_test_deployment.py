#!/usr/bin/env python3
"""
集成测试：Docker 部署验证
验证所有容器启动成功并且健康检查通过
"""

import subprocess
import time
import sys

def run_command(cmd):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"

def test_containers_running():
    """测试所有容器是否运行"""
    print("测试 1: 检查容器状态...")
    
    success, stdout, stderr = run_command("docker-compose ps")
    
    if not success:
        print(f"❌ 失败: 无法获取容器状态")
        print(f"错误: {stderr}")
        return False
    
    # 检查必需的容器
    required_containers = ["pmt-mysql", "pmt-backend", "pmt-frontend"]
    for container in required_containers:
        if container not in stdout:
            print(f"❌ 失败: 容器 {container} 未运行")
            return False
    
    print("✅ 通过: 所有容器正在运行")
    return True

def test_containers_healthy():
    """测试容器健康状态"""
    print("\n测试 2: 检查容器健康状态...")
    
    # 等待健康检查完成
    print("等待健康检查完成（最多 60 秒）...")
    max_wait = 60
    waited = 0
    
    while waited < max_wait:
        success, stdout, stderr = run_command("docker ps --format '{{.Names}}\t{{.Status}}'")
        
        if not success:
            print(f"❌ 失败: 无法获取容器状态")
            return False
        
        # 检查是否所有容器都健康
        lines = stdout.strip().split('\n')
        all_healthy = True
        
        for line in lines:
            if 'pmt-' in line:
                if 'starting' in line.lower():
                    all_healthy = False
                    break
        
        if all_healthy:
            break
        
        time.sleep(5)
        waited += 5
        print(f"等待中... ({waited}s)")
    
    # 最终检查
    success, stdout, stderr = run_command("docker ps --format '{{.Names}}\t{{.Status}}'")
    
    if not success:
        print(f"❌ 失败: 无法获取容器状态")
        return False
    
    print("\n容器状态:")
    print(stdout)
    
    # 检查是否有 unhealthy 状态
    if 'unhealthy' in stdout.lower():
        print("❌ 失败: 存在不健康的容器")
        return False
    
    print("✅ 通过: 所有容器健康")
    return True

def test_health_endpoint():
    """测试健康检查端点"""
    print("\n测试 3: 测试健康检查端点...")
    
    success, stdout, stderr = run_command("curl -f http://localhost/health")
    
    if not success:
        print(f"❌ 失败: 健康检查端点不可访问")
        print(f"错误: {stderr}")
        return False
    
    if 'status' not in stdout.lower():
        print(f"❌ 失败: 健康检查响应格式错误")
        print(f"响应: {stdout}")
        return False
    
    print(f"响应: {stdout}")
    print("✅ 通过: 健康检查端点正常")
    return True

def test_api_docs():
    """测试 API 文档可访问"""
    print("\n测试 4: 测试 API 文档...")
    
    success, stdout, stderr = run_command("curl -f http://localhost/api/docs")
    
    if not success:
        print(f"❌ 失败: API 文档不可访问")
        print(f"错误: {stderr}")
        return False
    
    if 'swagger' not in stdout.lower() and 'openapi' not in stdout.lower():
        print(f"❌ 失败: API 文档内容异常")
        return False
    
    print("✅ 通过: API 文档可访问")
    return True

def test_volumes_exist():
    """测试数据卷是否创建"""
    print("\n测试 5: 检查数据卷...")
    
    success, stdout, stderr = run_command("docker volume ls")
    
    if not success:
        print(f"❌ 失败: 无法获取数据卷列表")
        return False
    
    required_volumes = ["mysql-data", "attachments", "labels-data"]
    for volume in required_volumes:
        if volume not in stdout:
            print(f"❌ 失败: 数据卷 {volume} 不存在")
            return False
    
    print("✅ 通过: 所有数据卷已创建")
    return True

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Docker 部署集成测试")
    print("=" * 60)
    
    tests = [
        test_containers_running,
        test_containers_healthy,
        test_health_endpoint,
        test_api_docs,
        test_volumes_exist,
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
        print("1. docker-compose up -d 是否成功执行")
        print("2. 查看容器日志: docker-compose logs")
        print("3. 检查 .env 配置文件")
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过！部署成功！")
        sys.exit(0)

if __name__ == "__main__":
    main()
