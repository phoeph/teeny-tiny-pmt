#!/usr/bin/env python3
"""
Docker 配置简单验证脚本（无外部依赖）
Property 1: Docker Compose 配置完整性
Validates: Requirements 2.1, 2.2
"""
from pathlib import Path


def verify_files_exist():
    """验证所有必需文件存在"""
    print("🔍 验证 Docker 相关文件...")
    
    base_dir = Path(__file__).parents[2]
    
    files_to_check = [
        ("docker-compose.yml", base_dir / "docker-compose.yml"),
        (".env.example", base_dir / ".env.example"),
        ("backend/Dockerfile", base_dir / "backend" / "Dockerfile"),
        ("backend/docker/mysql-init.sql", base_dir / "backend" / "docker" / "mysql-init.sql"),
        ("nginx.conf", base_dir / "nginx.conf"),
    ]
    
    all_exist = True
    for name, path in files_to_check:
        if path.exists():
            print(f"✅ {name} 存在")
        else:
            print(f"❌ {name} 不存在")
            all_exist = False
    
    return all_exist


def verify_docker_compose_content():
    """验证 docker-compose.yml 内容"""
    print("\n🔍 验证 docker-compose.yml 内容...")
    
    compose_file = Path(__file__).parents[2] / "docker-compose.yml"
    with open(compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需的服务
    required_services = ['mysql:', 'backend:', 'frontend:']
    for service in required_services:
        if service in content:
            print(f"✅ 服务 {service[:-1]} 已定义")
        else:
            print(f"❌ 服务 {service[:-1]} 未定义")
            return False
    
    # 检查必需的配置项
    required_configs = [
        'restart: unless-stopped',
        'volumes:',
        'networks:',
        'pmt-network',
        'mysql-data',
        'attachments',
        'labels-data',
        'healthcheck:',
        'depends_on:',
    ]
    
    for config in required_configs:
        if config in content:
            print(f"✅ 配置项 '{config}' 存在")
        else:
            print(f"❌ 配置项 '{config}' 不存在")
            return False
    
    return True


def verify_dockerfile_content():
    """验证 Dockerfile 内容"""
    print("\n🔍 验证 backend/Dockerfile 内容...")
    
    dockerfile = Path(__file__).parents[2] / "backend" / "Dockerfile"
    with open(dockerfile, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_items = [
        'FROM python:3.11',
        'WORKDIR /app',
        'COPY requirements.txt',
        'RUN pip install',
        'EXPOSE 8000',
        'CMD',
        'uvicorn',
    ]
    
    for item in required_items:
        if item in content:
            print(f"✅ Dockerfile 包含 '{item}'")
        else:
            print(f"❌ Dockerfile 缺少 '{item}'")
            return False
    
    return True


def verify_env_example():
    """验证 .env.example 内容"""
    print("\n🔍 验证 .env.example 内容...")
    
    env_file = Path(__file__).parents[2] / ".env.example"
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_vars = [
        'MYSQL_ROOT_PASSWORD',
        'MYSQL_DATABASE',
        'MYSQL_USER',
        'MYSQL_PASSWORD',
        'SECRET_KEY',
        'LABELS_EXCEL_PATH',
    ]
    
    for var in required_vars:
        if var in content:
            print(f"✅ 环境变量 '{var}' 已定义")
        else:
            print(f"❌ 环境变量 '{var}' 未定义")
            return False
    
    return True


def verify_nginx_config():
    """验证 nginx.conf 内容"""
    print("\n🔍 验证 nginx.conf 内容...")
    
    nginx_file = Path(__file__).parents[2] / "nginx.conf"
    with open(nginx_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_items = [
        'location /api/',
        'proxy_pass http://pmt-backend:8000',
        'location /health',
    ]
    
    for item in required_items:
        if item in content:
            print(f"✅ Nginx 配置包含 '{item}'")
        else:
            print(f"❌ Nginx 配置缺少 '{item}'")
            return False
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("Docker 配置验证")
    print("Property 1: Docker Compose 配置完整性")
    print("Validates: Requirements 2.1, 2.2")
    print("="*60 + "\n")
    
    try:
        results = []
        results.append(verify_files_exist())
        results.append(verify_docker_compose_content())
        results.append(verify_dockerfile_content())
        results.append(verify_env_example())
        results.append(verify_nginx_config())
        
        if all(results):
            print("\n" + "="*60)
            print("🎉 所有 Docker 配置验证通过！")
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
