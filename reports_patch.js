// 这是对reports.html中renderProjectGroups函数的补丁
// 需要手动将此代码替换到reports.html中的renderProjectGroups函数

function renderProjectGroups(projectGroups) {
  if (!projectGroups || Object.keys(projectGroups).length === 0) {
    return '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">暂无任务数据</div>';
  }
  
  let html = '';
  let projectIndex = 1;
  
  Object.values(projectGroups).forEach(pg => {
    const projectProgress = pg.stats.total > 0 
      ? Math.round(pg.stats.done / pg.stats.total * 100) 
      : 0;
    const projectProgressColor = projectProgress >= 100 ? 'var(--success)' : (projectProgress >= 50 ? 'var(--warning)' : 'var(--text-secondary)');
    
    html += `
      <div class="category-section" style="margin-bottom: 32px;">
        <h4 style="font-size: 16px; font-weight: 600; color: var(--text-main); margin-bottom: 16px; padding-left: 12px; border-left: 4px solid var(--primary);">
          <span>${numberToChinese(projectIndex)}、${pg.projectName}</span>
        </h4>
    `;
    
    if (Object.keys(pg.labelHierarchy).length === 0) {
      html += '<div style="margin-left: 20px; color: var(--text-secondary);">暂无任务</div>';
    } else {
      let firstLevelIndex = 1;
      
      // 渲染第一级标签
      Object.values(pg.labelHierarchy).forEach(firstLevel => {
        const firstLevelProgress = firstLevel.stats.total > 0 
          ? Math.round(firstLevel.stats.done / firstLevel.stats.total * 100) 
          : 0;
        const firstLevelProgressColor = firstLevelProgress >= 100 ? 'var(--success)' : (firstLevelProgress >= 50 ? 'var(--warning)' : 'var(--text-secondary)');
        
        html += `
          <div style="margin-left: 20px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; margin-bottom: 16px; padding: 10px 16px; background: #f8fafc; border-radius: 8px; border-left: 3px solid var(--primary);">
              <span style="font-size: 15px; font-weight: 600; color: var(--text-main);">
                ${firstLevelIndex}. ${firstLevel.name}
              </span>
            </div>
        `;
        
        let lastLevelIndex = 1;
        
        // 渲染最后一级标签
        Object.values(firstLevel.children).forEach(lastLevel => {
          const lastLevelProgress = lastLevel.stats.total > 0 
            ? Math.round(lastLevel.stats.done / lastLevel.stats.total * 100) 
            : 0;
          const lastLevelProgressColor = lastLevelProgress >= 100 ? 'var(--success)' : (lastLevelProgress >= 50 ? 'var(--warning)' : 'var(--text-secondary)');
          
          html += `
            <div style="margin-left: 20px; margin-bottom: 20px;">
              <div style="display: flex; align-items: center; margin-bottom: 12px; padding: 8px 12px; background: #f8fafc; border-radius: 6px;">
                <span style="font-size: 14px; font-weight: 600; color: var(--text-main);">
                  (${lastLevelIndex}) ${lastLevel.name}
                </span>
              </div>
              
              <div style="margin-left: 20px;">
                <div style="margin: 0; padding-left: 0; list-style: none;">
          `;
          
          lastLevel.tasks.forEach((task, idx) => {
            const statusClass = `status-${task.status || 'todo'}`;
            const statusText = getStatusText(task.status);
            const taskProgress = calculateTaskProgress(task);
            const taskProgressColor = taskProgress >= 100 ? 'var(--success)' : (taskProgress >= 50 ? 'var(--warning)' : 'var(--text-secondary)');
            
            html += `
                  <div style="display: flex; align-items: center; gap: 12px; padding: 8px 12px; margin-bottom: 6px; background: var(--bg-surface); border-radius: 6px;">
                    <span style="color: var(--text-secondary); font-size: 12px; min-width: 20px;">${idx + 1}.</span>
                    <span style="flex: 1; color: var(--text-main); font-size: 13px;">${task.title || task.name || task.code || '未命名任务'}</span>
                    <div style="display: flex; align-items: center; gap: 6px; min-width: 80px;">
                      <div style="flex: 1; max-width: 40px; height: 4px; background: var(--border-light); border-radius: 2px; overflow: hidden;">
                        <div style="width: ${taskProgress}%; height: 100%; background: ${taskProgressColor}; border-radius: 2px;"></div>
                      </div>
                      <span style="color: ${taskProgressColor}; font-weight: 600; font-size: 11px; min-width: 28px;">${taskProgress}%</span>
                    </div>
                    <span class="status-badge ${statusClass}" style="font-size: 9px; padding: 2px 8px; flex-shrink: 0;">${statusText}</span>
                  </div>
            `;
          });
          
          html += `
                </div>
              </div>
            </div>
          `;
          lastLevelIndex++;
        });
        
        html += '</div>';
        firstLevelIndex++;
      });
    }
    
    // 添加非开发工作说明
    if (pg.nonDevWorks && pg.nonDevWorks.length > 0) {
      html += `
        <div style="margin-left: 20px; margin-bottom: 24px;">
          <div style="display: flex; align-items: center; margin-bottom: 16px; padding: 10px 16px; background: #f0f9ff; border-radius: 8px; border-left: 3px solid var(--primary);">
            <span style="font-size: 15px; font-weight: 600; color: var(--text-main);">
              ${firstLevelIndex}. 其他非开发工作说明
            </span>
          </div>
          
          <div style="margin-left: 20px;">
            <div style="margin: 0; padding-left: 0; list-style: none;">
      `;
      
      pg.nonDevWorks.forEach((work, idx) => {
        html += `
              <div style="display: flex; align-items: flex-start; gap: 12px; padding: 8px 12px; margin-bottom: 6px; background: var(--bg-surface); border-radius: 6px;">
                <span style="color: var(--text-secondary); font-size: 12px; min-width: 20px; margin-top: 2px;">${idx + 1}.</span>
                <div style="flex: 1;">
                  <div style="color: var(--text-main); font-size: 13px; font-weight: 500; margin-bottom: 4px;">${work.title || '未命名工作'}</div>
                  ${work.description ? `<div style="color: var(--text-secondary); font-size: 12px; line-height: 1.4;">${work.description}</div>` : ''}
                </div>
              </div>
        `;
      });
      
      html += `
            </div>
          </div>
        </div>
      `;
    }
    
    html += '</div>';
    projectIndex++;
  });
  
  return html;
}