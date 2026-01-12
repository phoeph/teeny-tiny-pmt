// 版本信息 - 用于防止缓存问题
window.APP_VERSION = {
    version: '1.0.0',
    buildTime: new Date().toISOString(),
    gitCommit: '4b83402', // 最新提交 hash
    description: '项目管理工具 - 最新版本'
};

// 在控制台显示版本信息
console.log('🚀 项目管理系统已加载');
console.log('📦 版本:', window.APP_VERSION.version);
console.log('🕒 构建时间:', window.APP_VERSION.buildTime);
console.log('📝 提交:', window.APP_VERSION.gitCommit);