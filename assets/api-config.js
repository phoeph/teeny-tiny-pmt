// API配置 - 自动检测后端地址
(function() {
  // 获取当前页面的协议和主机
  const protocol = window.location.protocol; // http: 或 https:
  const hostname = window.location.hostname; // localhost 或 124.220.35.110
  const port = window.location.port; // 端口号（如果有）
  
  // 构建基础 URL
  const baseUrl = port ? `${protocol}//${hostname}:${port}` : `${protocol}//${hostname}`;
  
  // API 路径（通过 Nginx 代理，不需要指定后端端口）
  const API_BASE = `${baseUrl}/api`;
  
  // 导出到全局
  window.API_CONFIG = {
    API: API_BASE,
    BASE_URL: baseUrl
  };
  
  console.log('[API Config] Backend URL:', API_BASE);
})();
