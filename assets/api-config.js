// API配置 - 自动检测后端地址
(function() {
  // 获取当前页面的协议和主机
  const protocol = window.location.protocol; // http: 或 https:
  const hostname = window.location.hostname; // localhost 或 124.220.35.110
  const port = window.location.port; // 端口号（如果有）
  
  // 智能检测环境：
  // 1. 本地开发：localhost 或 127.0.0.1，使用 :8000
  // 2. Docker 部署：通过 Nginx 代理，使用当前端口（通常是 80）
  const isLocalDev = hostname === 'localhost' || hostname === '127.0.0.1';
  
  let API_BASE;
  let BASE_URL;
  
  if (isLocalDev) {
    // 本地开发环境：直接访问后端 8000 端口
    API_BASE = `${protocol}//${hostname}:8000/api`;
    BASE_URL = `${protocol}//${hostname}:8000`;
  } else {
    // 生产环境：通过 Nginx 代理
    BASE_URL = port ? `${protocol}//${hostname}:${port}` : `${protocol}//${hostname}`;
    API_BASE = `${BASE_URL}/api`;
  }
  
  // 导出到全局
  window.API_CONFIG = {
    API: API_BASE,
    BASE_URL: BASE_URL
  };
  
  console.log('[API Config] Environment:', isLocalDev ? 'Local Dev' : 'Production');
  console.log('[API Config] Backend URL:', API_BASE);
})();
