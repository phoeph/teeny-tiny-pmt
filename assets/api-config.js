// API配置 - 统一使用 8000 端口
(function() {
  // 获取当前页面的协议和主机
  const protocol = window.location.protocol; // http: 或 https:
  const hostname = window.location.hostname; // localhost 或 124.220.35.110
  
  // 统一使用 8000 端口（本地开发和生产环境一致）
  const BASE_URL = `${protocol}//${hostname}:8000`;
  const API_BASE = `${BASE_URL}/api`;
  
  // 导出到全局
  window.API_CONFIG = {
    API: API_BASE,
    BASE_URL: BASE_URL
  };
  
  // 兼容旧代码：同时导出 window.API
  window.API = API_BASE;
  
  console.log('[API Config] Backend URL:', API_BASE);
})();
