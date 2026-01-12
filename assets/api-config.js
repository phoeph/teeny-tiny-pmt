// API配置 - 自动检测后端地址
(function() {
  // 获取当前页面的协议和主机
  const protocol = window.location.protocol; // http: 或 https:
  const hostname = window.location.hostname; // localhost 或 192.168.18.41
  
  // 后端端口固定为8000
  const API_BASE = `${protocol}//${hostname}:8000/api`;
  
  // 导出到全局
  window.API_CONFIG = {
    API: API_BASE,
    BASE_URL: `${protocol}//${hostname}:8000`
  };
  
  console.log('[API Config] Backend URL:', API_BASE);
})();
