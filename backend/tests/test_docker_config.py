"""
Docker 配置验证测试
Property 1: Docker Compose 配置完整性
Validates: Requirements 2.1, 2.2
"""
import yaml
import pytest
from pathlib import Path


def load_docker_compose():
    """加载 docker-compose.yml 文件"""
    compose_file = Path(__file__).parents[2] / "docker-compose.yml"
    with open(compose_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_docker_compose_file_exists():
    """测试 docker-compose.yml 文件存在"""
    compose_file = Path(__file__).parents[2] / "docker-compose.yml"
    assert compose_file.exists(), "docker-compose.yml file not found"


def test_docker_compose_has_required_services():
    """
    Property 1: Docker Compose 配置完整性
    验证 docker-compose.yml 包含所有必需服务：MySQL、后端、前端
    """
    config = load_docker_compose()
    
    # 验证 services 部分存在
    assert 'services' in config, "docker-compose.yml must have 'services' section"
    
    services = config['services']
    
    # 验证三个核心服务存在
    required_services = ['mysql', 'backend', 'frontend']
    for service in required_services:
        assert service in services, f"Service '{service}' not found in docker-compose.yml"


def test_mysql_service_configuration():
    """验证 MySQL 服务配置正确"""
    config = load_docker_compose()
    mysql = config['services']['mysql']
    
    # 验证镜像
    assert 'image' in mysql, "MySQL service must specify an image"
    assert 'mysql' in mysql['image'].lower(), "MySQL service must use MySQL image"
    
    # 验证环境变量
    assert 'environment' in mysql, "MySQL service must have environment variables"
    env = mysql['environment']
    required_env_vars = ['MYSQL_ROOT_PASSWORD', 'MYSQL_DATABASE', 'MYSQL_USER', 'MYSQL_PASSWORD']
    for var in required_env_vars:
        assert var in env, f"MySQL service must have {var} environment variable"
    
    # 验证数据卷
    assert 'volumes' in mysql, "MySQL service must have volumes"
    volumes = mysql['volumes']
    assert any('mysql-data' in str(v) for v in volumes), "MySQL service must mount mysql-data volume"
    
    # 验证健康检查
    assert 'healthcheck' in mysql, "MySQL service must have healthcheck"
    
    # 验证重启策略
    assert 'restart' in mysql, "MySQL service must have restart policy"
    assert mysql['restart'] == 'unless-stopped', "MySQL restart policy should be 'unless-stopped'"


def test_backend_service_configuration():
    """验证后端服务配置正确"""
    config = load_docker_compose()
    backend = config['services']['backend']
    
    # 验证构建配置
    assert 'build' in backend, "Backend service must have build configuration"
    
    # 验证环境变量
    assert 'environment' in backend, "Backend service must have environment variables"
    env = backend['environment']
    required_env_vars = ['DATABASE_URL', 'SECRET_KEY', 'LABELS_EXCEL_PATH']
    for var in required_env_vars:
        assert var in env, f"Backend service must have {var} environment variable"
    
    # 验证数据卷
    assert 'volumes' in backend, "Backend service must have volumes"
    volumes = backend['volumes']
    assert any('attachments' in str(v) for v in volumes), "Backend must mount attachments volume"
    assert any('labels-data' in str(v) for v in volumes), "Backend must mount labels-data volume"
    
    # 验证依赖关系
    assert 'depends_on' in backend, "Backend service must depend on MySQL"
    
    # 验证健康检查
    assert 'healthcheck' in backend, "Backend service must have healthcheck"
    
    # 验证重启策略
    assert 'restart' in backend, "Backend service must have restart policy"
    assert backend['restart'] == 'unless-stopped', "Backend restart policy should be 'unless-stopped'"


def test_frontend_service_configuration():
    """验证前端服务配置正确"""
    config = load_docker_compose()
    frontend = config['services']['frontend']
    
    # 验证镜像
    assert 'image' in frontend, "Frontend service must specify an image"
    assert 'nginx' in frontend['image'].lower(), "Frontend service must use Nginx image"
    
    # 验证端口映射
    assert 'ports' in frontend, "Frontend service must expose ports"
    ports = frontend['ports']
    assert any('80' in str(p) for p in ports), "Frontend must expose port 80"
    
    # 验证数据卷（nginx 配置和静态文件）
    assert 'volumes' in frontend, "Frontend service must have volumes"
    
    # 验证依赖关系
    assert 'depends_on' in frontend, "Frontend service must depend on backend"
    
    # 验证重启策略
    assert 'restart' in frontend, "Frontend service must have restart policy"
    assert frontend['restart'] == 'unless-stopped', "Frontend restart policy should be 'unless-stopped'"


def test_volumes_configuration():
    """验证数据卷配置正确"""
    config = load_docker_compose()
    
    # 验证 volumes 部分存在
    assert 'volumes' in config, "docker-compose.yml must have 'volumes' section"
    
    volumes = config['volumes']
    
    # 验证必需的数据卷
    required_volumes = ['mysql-data', 'attachments', 'labels-data']
    for volume in required_volumes:
        assert volume in volumes, f"Volume '{volume}' not found in docker-compose.yml"


def test_network_configuration():
    """验证网络配置正确"""
    config = load_docker_compose()
    
    # 验证 networks 部分存在
    assert 'networks' in config, "docker-compose.yml must have 'networks' section"
    
    networks = config['networks']
    
    # 验证 pmt-network 存在
    assert 'pmt-network' in networks, "Network 'pmt-network' not found"
    
    # 验证所有服务都连接到网络
    services = config['services']
    for service_name, service_config in services.items():
        assert 'networks' in service_config, f"Service '{service_name}' must be connected to a network"
        assert 'pmt-network' in service_config['networks'], f"Service '{service_name}' must be connected to pmt-network"


def test_service_dependencies():
    """验证服务依赖顺序正确"""
    config = load_docker_compose()
    services = config['services']
    
    # 后端依赖 MySQL
    backend_deps = services['backend'].get('depends_on', {})
    assert 'mysql' in backend_deps, "Backend must depend on MySQL"
    
    # 前端依赖后端
    frontend_deps = services['frontend'].get('depends_on', [])
    assert 'backend' in frontend_deps, "Frontend must depend on backend"


def test_env_example_file_exists():
    """测试 .env.example 文件存在"""
    env_example = Path(__file__).parents[2] / ".env.example"
    assert env_example.exists(), ".env.example file not found"


def test_dockerfile_exists():
    """测试后端 Dockerfile 存在"""
    dockerfile = Path(__file__).parents[1] / "Dockerfile"
    assert dockerfile.exists(), "backend/Dockerfile not found"


def test_mysql_init_script_exists():
    """测试 MySQL 初始化脚本存在"""
    init_script = Path(__file__).parents[1] / "docker" / "mysql-init.sql"
    assert init_script.exists(), "backend/docker/mysql-init.sql not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
