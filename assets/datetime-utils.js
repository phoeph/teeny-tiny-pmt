/**
 * 全局时间格式化工具 - 统一使用东八区 (UTC+8)
 */
(function() {
  // 格式化为东八区时间 (完整格式: YYYY-MM-DD HH:mm:ss)
  function formatCST(s) {
    try {
      if (!s) return '';
      var d = new Date(s);
      if (isNaN(d.getTime())) return String(s || '');
      // 转换为东八区时间
      var cst = new Date(d.getTime() + 8 * 60 * 60 * 1000);
      var y = cst.getUTCFullYear();
      var m = String(cst.getUTCMonth() + 1).padStart(2, '0');
      var dd = String(cst.getUTCDate()).padStart(2, '0');
      var hh = String(cst.getUTCHours()).padStart(2, '0');
      var mm = String(cst.getUTCMinutes()).padStart(2, '0');
      var ss = String(cst.getUTCSeconds()).padStart(2, '0');
      return y + '-' + m + '-' + dd + ' ' + hh + ':' + mm + ':' + ss;
    } catch (_) {
      return String(s || '');
    }
  }

  // 格式化为东八区时间 (短格式: YYYY-MM-DD HH:mm)
  function formatCSTShort(s) {
    try {
      if (!s) return '';
      var d = new Date(s);
      if (isNaN(d.getTime())) return String(s || '');
      var cst = new Date(d.getTime() + 8 * 60 * 60 * 1000);
      var y = cst.getUTCFullYear();
      var m = String(cst.getUTCMonth() + 1).padStart(2, '0');
      var dd = String(cst.getUTCDate()).padStart(2, '0');
      var hh = String(cst.getUTCHours()).padStart(2, '0');
      var mm = String(cst.getUTCMinutes()).padStart(2, '0');
      return y + '-' + m + '-' + dd + ' ' + hh + ':' + mm;
    } catch (_) {
      return String(s || '');
    }
  }

  // 格式化为东八区日期 (仅日期: YYYY-MM-DD)
  function formatCSTDate(s) {
    try {
      if (!s) return '';
      var d = new Date(s);
      if (isNaN(d.getTime())) return String(s || '');
      var cst = new Date(d.getTime() + 8 * 60 * 60 * 1000);
      var y = cst.getUTCFullYear();
      var m = String(cst.getUTCMonth() + 1).padStart(2, '0');
      var dd = String(cst.getUTCDate()).padStart(2, '0');
      return y + '-' + m + '-' + dd;
    } catch (_) {
      return String(s || '');
    }
  }

  // 暴露到全局
  window.DateTimeUtils = {
    formatCST: formatCST,
    formatCSTShort: formatCSTShort,
    formatCSTDate: formatCSTDate
  };

  // 兼容旧代码的全局函数
  window.__fmtCST = formatCST;
  window.__fmtCSTShort = formatCSTShort;
  window.__fmtCSTDate = formatCSTDate;
})();
