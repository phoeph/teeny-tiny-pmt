#!/usr/bin/env python3
"""
Docker 配置验证脚本（不依赖 pytest）
Property 1: Docker Compose 配置完整性
Validates: Requirements 2.1, 2.2
"""
import yaml
from pathlib import Path


def load_docker_compose():
    """加载 docker-compose.yml 文件"""
    compose_file = Path(__file__).parents[2] / "docker-compose.yml"
    with open(compose_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def verify_docker_compose_structure():
    """验证 Docker Compose 配置完整性"""
    print("🔍 验证 Docker Compose 配置...")
    
    # 检查文件存在
    compose_file = Path(__file__).parents[2] / "docker-compose.yml"
    assert compose_file.exists(), "❌ docker-compose.yml 文件不存在"
    print("✅ docker-compose.yml 文件存在")
    
    # 加载配置
    config = load_docker_compose()
    
    # 验证 services
    assert 'services' in config, "❌ 缺少 services 部分"
    print("✅ services 部分存在")
    
    services = config['services']
    required_services = ['mysql', 'backend', 'frontend']
    for service in required_services:
        assert service in services, f"❌ 缺少服务: {service}"
        print(f"✅ 服务 '{service}' 存在")
    
    # 验证 MySQL 配置
    mysql = services['mysql']
    assert 'image' in mysql and 'mysql' in mysql['image'].lower(), "❌ MySQL 镜像配置错误"
    assert 'environment' in mysql, "❌ MySQL 缺少环境变量"
    assert 'volumes' in mysql, "❌ MySQL 缺少数据卷"
    assert 'healthcheck' in mysql, "❌ MySQL 缺少健康检查"
    assert mysql.get('restart') == 'unless-stopped', "❌ MySQL 重启策略错误"
    print("✅ MySQL 服务配置正确")
    
    # 验证后端配置
    backend = services['backend']
    assert 'build' in backend, "❌ 后端缺少构建配置"
    assert 'environment' in backend, "❌ 后端缺少环境变量"
    assert 'volumes' in backend, "❌ 后端缺少数据卷"
    assert 'depends_on' in backend, "❌ 后端缺少依赖配置"
    assert 'healthcheck' in backend, "❌ 后端缺少健康检查"
    assert backend.get('restart') == 'unless-stopped', "❌ 后端重启策略错误"
    print("✅ 后端服务配置正确")
    
    # 验证前端配置
    frontend = services['frontend']
    assert 'image' in frontend and 'nginx' in frontend['image'].lower(), "❌ 前端镜像配置错误"
    assert 'ports' in frontend, "❌ 前端缺少端口映射"
    assert 'volumes' in frontend, "❌ 前端缺少数据卷"
    assert 'depends_on' in frontend, "❌ 前端缺少依赖配置"
    assert frontend.get('restart') == 'unless-stopped', "❌ 前端重启策略错误"
    print("✅ 前端服务配置正确")
    
    # 验证数据卷
    assert 'volumes' in config, "❌ 缺少 volumes 部分"
    volumes = config['volumes']
    required_volumes = ['mysql-data', 'attachments', 'labels-data']
    for volume in required_volumes:
        assert volume in volumes, f"❌ 缺少数据卷: {volume}"
        print(f"✅ 数据卷 '{volume}' 存在")
    
    # 验证网络
    assert 'networks' in config, "❌ 缺少 networks 部分"
    networks = config['networks']
    assert 'pmt-network' in networks, "❌ 缺少 pmt-network 网络"
    print("✅ 网络配置正确")
    
    # 验证服务依赖
    assert 'mysql' in backend.get('depends_on', {}), "❌ 后端未依赖 MySQL"
    assert 'backend' in frontend.get('depends_on', []), "❌ 前端未依赖后端"
    print("✅ 服务依赖关系正确")
    
    print("\n✅ 所有 Docker Compose 配置验证通过！")


def verify_supporting_files():
    """验证支持文件存在"""
    print("\n🔍 验证支持文件...")
    
    base_dir = Path(__file__).parents[2]
    
    # 检查 .env.example
    env_example = base_dir / ".env.example"
    assert env_example.exists(), "❌ .env.example 文件不存在"
    print("✅ .env.example 文件存在")
    
    # 检查 Dockerfile
    dockerfile = base_dir / "backend" / "Dockerfile"
    assert dockerfile.exists(), "❌ backend/Dockerfile 不存在"
    print("✅ backend/Dockerfile 存在")
    
    # 检查 MySQL 初始化脚本
    init_script = base_dir / "backend" / "docker" / "mysql-init.sql"
    assert init_script.exists(), "❌ backend/docker/mysql-init.sql 不存在"
    print("✅ backend/docker/mysql-init.sql 存在")
    
    # 检查 nginx.conf
    nginx_conf = base_dir / "nginx.conf"
    assert nginx_conf.exists(), "❌ nginx.conf 不存在"
    print("✅ nginx.conf 存在")
    
    print("\n✅ 所有支持文件验证通过！")


if __name__ == "__main__":
    try:
        verify_docker_compose_structure()
        verify_supporting_files()
        print("\n" + "="*50)
        print("🎉 Docker 配置验证全部通过！")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ 验证失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        exit(1)
