/**
 * 周报非开发工作管理组件
 * 用于在周报页面管理非开发工作说明
 */

class ReportNonDevWorkManager {
  constructor(apiBase = 'http://localhost:8000/api') {
    this.apiBase = apiBase;
    this.token = localStorage.getItem('token');
    this.nonDevWorks = [];
    this.selectedProjects = [];
    this.reportStartDate = null;
    this.reportEndDate = null;
    this.isEditing = false;
    this.editingId = null;
  }

  /**
   * 初始化组件
   */
  async init(selectedProjects, startDate, endDate) {
    this.selectedProjects = selectedProjects || [];
    this.reportStartDate = startDate;
    this.reportEndDate = endDate;
    
    if (this.selectedProjects.length > 0 && this.reportStartDate && this.reportEndDate) {
      await this.loadNonDevWorks();
    }
    
    this.render();
    this.bindEvents();
  }

  /**
   * 更新报告参数
   */
  async updateReportParams(selectedProjects, startDate, endDate) {
    this.selectedProjects = selectedProjects || [];
    this.reportStartDate = startDate;
    this.reportEndDate = endDate;
    
    if (this.selectedProjects.length > 0 && this.reportStartDate && this.reportEndDate) {
      await this.loadNonDevWorks();
    } else {
      this.nonDevWorks = [];
    }
    
    this.render();
    this.bindEvents();
  }

  /**
   * 加载非开发工作列表
   */
  async loadNonDevWorks() {
    if (!this.selectedProjects.length || !this.reportStartDate || !this.reportEndDate) {
      this.nonDevWorks = [];
      return;
    }

    try {
      const projectIds = this.selectedProjects.join(',');
      const params = new URLSearchParams({
        project_ids: projectIds,
        start_date: this.reportStartDate,
        end_date: this.reportEndDate
      });

      const response = await fetch(`${this.apiBase}/non-dev-works/by-report?${params}`, {
        headers: { Authorization: `Bearer ${this.token}` }
      });
      
      if (response.status === 401) {
        // Token expired or invalid, redirect to login
        localStorage.removeItem('token');
        window.location.href = 'login.html';
        return;
      }
      
      if (response.ok) {
        this.nonDevWorks = await response.json();
      } else {
        console.error('Failed to load non-dev works:', response.status);
        this.nonDevWorks = [];
      }
    } catch (error) {
      console.error('Error loading non-dev works:', error);
      this.nonDevWorks = [];
    }
  }

  /**
   * 渲染组件
   */
  render() {
    const container = document.getElementById('reportNonDevWorkContainer');
    if (!container) return;

    if (!this.selectedProjects.length || !this.reportStartDate || !this.reportEndDate) {
      container.innerHTML = `
        <div class="non-dev-work-section" style="display: none;">
          <div class="section-header">
            <h4>其他非开发工作说明</h4>
            <button class="primary-btn btn-sm" id="addReportNonDevWorkBtn" disabled>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              添加说明
            </button>
          </div>
          <div class="empty-state">
            <p>请先选择项目和时间范围</p>
          </div>
        </div>
        <div class="non-dev-work-section" style="display: none;">
          <div class="section-header">
            <h4>下周工作计划</h4>
            <button class="primary-btn btn-sm" id="addReportNextWeekPlanBtn" disabled>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              添加计划
            </button>
          </div>
          <div class="empty-state">
            <p>请先选择项目和时间范围</p>
          </div>
        </div>
      `;
      return;
    }

    // 按工作类型分组
    const otherWorks = this.nonDevWorks.filter(w => w.work_type === 'other_work');
    const nextWeekPlans = this.nonDevWorks.filter(w => w.work_type === 'next_week_plan');

    const html = `
      <!-- 其他非开发工作说明 -->
      <div class="non-dev-work-section">
        <div class="section-header">
          <h4>其他非开发工作说明</h4>
          <button class="primary-btn btn-sm" id="addReportNonDevWorkBtn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            添加说明
          </button>
        </div>
        
        <div class="non-dev-work-list" id="reportNonDevWorkList">
          ${this.renderNonDevWorkList(otherWorks)}
        </div>
      </div>
      
      <!-- 下周工作计划 -->
      <div class="non-dev-work-section">
        <div class="section-header">
          <h4>下周工作计划</h4>
          <button class="primary-btn btn-sm" id="addReportNextWeekPlanBtn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            添加计划
          </button>
        </div>
        
        <div class="non-dev-work-list" id="reportNextWeekPlanList">
          ${this.renderNonDevWorkList(nextWeekPlans)}
        </div>
      </div>
        
      <div class="non-dev-work-form" id="reportNonDevWorkForm" style="display: none;">
        <div class="form-header">
          <h4 id="reportNonDevWorkFormTitle">添加工作记录</h4>
        </div>
        
        <div class="form-group">
          <label>工作类型</label>
          <select id="reportNonDevWorkType">
            <option value="other_work">其他非开发工作说明</option>
            <option value="next_week_plan">下周工作计划</option>
          </select>
        </div>
        <div class="form-group">
          <label>所属项目</label>
          <select id="reportNonDevWorkProject">
            ${this.renderProjectOptions()}
          </select>
        </div>
        <div class="form-group">
          <label id="reportNonDevWorkTitleLabel">工作说明标题</label>
          <input type="text" id="reportNonDevWorkTitle" placeholder="例如：预估新需求工时并和政企领导汇报进度" />
        </div>
        <div class="form-group">
          <label>详细描述（可选）</label>
          <textarea id="reportNonDevWorkDescription" rows="3" placeholder="详细描述工作内容..."></textarea>
        </div>
        <div class="form-actions">
          <button class="ghost-btn" id="cancelReportNonDevWorkBtn">取消</button>
          <button class="primary-btn" id="saveReportNonDevWorkBtn">保存</button>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  /**
   * 渲染项目选项
   */
  renderProjectOptions() {
    if (!window.allProjects || !this.selectedProjects.length) {
      return '<option value="">请选择项目</option>';
    }

    const selectedProjectsData = window.allProjects.filter(p => 
      this.selectedProjects.includes(p.id)
    );

    return selectedProjectsData.map(project => 
      `<option value="${project.id}">${project.name || project.title || `项目 ${project.id}`}</option>`
    ).join('');
  }

  /**
   * 渲染非开发工作列表
   */
  renderNonDevWorkList(works = null) {
    const workList = works || this.nonDevWorks;
    
    if (workList.length === 0) {
      return `
        <div class="empty-state">
          <p>暂无记录</p>
        </div>
      `;
    }

    // 按项目分组
    const groupedWorks = {};
    workList.forEach(work => {
      if (!groupedWorks[work.project_id]) {
        groupedWorks[work.project_id] = [];
      }
      groupedWorks[work.project_id].push(work);
    });

    let html = '';
    Object.keys(groupedWorks).forEach(projectId => {
      const works = groupedWorks[projectId];
      const project = window.allProjects?.find(p => p.id === parseInt(projectId));
      const projectName = project ? (project.name || project.title || `项目 ${projectId}`) : `项目 ${projectId}`;

      html += `
        <div class="project-group">
          <h5 class="project-group-title">${projectName}</h5>
          <div class="project-works">
      `;

      works.forEach((work, index) => {
        const workTypeText = work.work_type === 'next_week_plan' ? '计划' : '说明';
        html += `
          <div class="non-dev-work-item" data-id="${work.id}">
            <div class="work-item-header">
              <span class="work-item-index">${index + 1}.</span>
              <span class="work-item-title">${this.escapeHtml(work.title)}</span>
              <div class="work-item-actions">
                <button class="btn-icon edit-report-work-btn" data-id="${work.id}" title="编辑">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button class="btn-icon delete-report-work-btn" data-id="${work.id}" title="删除">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"></polyline>
                    <path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2v2"></path>
                  </svg>
                </button>
              </div>
            </div>
            ${work.description ? `<div class="work-item-description">${this.escapeHtml(work.description)}</div>` : ''}
            <div class="work-item-period">报告期间: ${work.report_period_start} ~ ${work.report_period_end}</div>
          </div>
        `;
      });

      html += `
          </div>
        </div>
      `;
    });

    return html;
  }

  /**
   * 绑定事件
   */
  bindEvents() {
    // 添加其他非开发工作说明按钮
    const addBtn = document.getElementById('addReportNonDevWorkBtn');
    if (addBtn) {
      addBtn.addEventListener('click', () => this.showForm('other_work'));
    }

    // 添加下周工作计划按钮
    const addNextWeekBtn = document.getElementById('addReportNextWeekPlanBtn');
    if (addNextWeekBtn) {
      addNextWeekBtn.addEventListener('click', () => this.showForm('next_week_plan'));
    }

    // 工作类型选择变化
    const workTypeSelect = document.getElementById('reportNonDevWorkType');
    if (workTypeSelect) {
      workTypeSelect.addEventListener('change', () => this.updateFormLabels());
    }

    // 取消按钮
    const cancelBtn = document.getElementById('cancelReportNonDevWorkBtn');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.hideForm());
    }

    // 保存按钮
    const saveBtn = document.getElementById('saveReportNonDevWorkBtn');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => this.saveNonDevWork());
    }

    // 编辑和删除按钮
    const otherWorkContainer = document.getElementById('reportNonDevWorkList');
    const nextWeekContainer = document.getElementById('reportNextWeekPlanList');
    
    [otherWorkContainer, nextWeekContainer].forEach(container => {
      if (container) {
        container.addEventListener('click', (e) => {
          const editBtn = e.target.closest('.edit-report-work-btn');
          const deleteBtn = e.target.closest('.delete-report-work-btn');

          if (editBtn) {
            const workId = parseInt(editBtn.dataset.id);
            this.editNonDevWork(workId);
          } else if (deleteBtn) {
            const workId = parseInt(deleteBtn.dataset.id);
            this.deleteNonDevWork(workId);
          }
        });
      }
    });
  }

  /**
   * 显示表单
   */
  showForm(workType = 'other_work', work = null) {
    this.isEditing = !!work;
    this.editingId = work ? work.id : null;

    const form = document.getElementById('reportNonDevWorkForm');
    const workTypeSelect = document.getElementById('reportNonDevWorkType');
    const projectSelect = document.getElementById('reportNonDevWorkProject');
    const titleInput = document.getElementById('reportNonDevWorkTitle');
    const descInput = document.getElementById('reportNonDevWorkDescription');
    const formTitle = document.getElementById('reportNonDevWorkFormTitle');

    if (work) {
      workTypeSelect.value = work.work_type;
      projectSelect.value = work.project_id;
      titleInput.value = work.title;
      descInput.value = work.description || '';
      
      // 设置编辑模式的标题
      if (work.work_type === 'next_week_plan') {
        formTitle.textContent = '编辑下周工作计划';
      } else {
        formTitle.textContent = '编辑其他非开发工作说明';
      }
    } else {
      workTypeSelect.value = workType;
      projectSelect.value = this.selectedProjects[0] || '';
      titleInput.value = '';
      descInput.value = '';
    }

    this.updateFormLabels();
    form.style.display = 'block';
    titleInput.focus();
  }

  /**
   * 更新表单标签
   */
  updateFormLabels() {
    const workTypeSelect = document.getElementById('reportNonDevWorkType');
    const titleLabel = document.getElementById('reportNonDevWorkTitleLabel');
    const titleInput = document.getElementById('reportNonDevWorkTitle');
    const formTitle = document.getElementById('reportNonDevWorkFormTitle');
    
    if (workTypeSelect && titleLabel && titleInput && formTitle) {
      if (workTypeSelect.value === 'next_week_plan') {
        formTitle.textContent = '添加下周工作计划';
        titleLabel.textContent = '工作计划标题';
        titleInput.placeholder = '例如：完成用户管理模块开发';
      } else {
        formTitle.textContent = '添加其他非开发工作说明';
        titleLabel.textContent = '工作说明标题';
        titleInput.placeholder = '例如：预估新需求工时并和政企领导汇报进度';
      }
    }
  }

  /**
   * 隐藏表单
   */
  hideForm() {
    const form = document.getElementById('reportNonDevWorkForm');
    form.style.display = 'none';
    this.isEditing = false;
    this.editingId = null;
  }

  /**
   * 保存非开发工作
   */
  async saveNonDevWork() {
    const workTypeSelect = document.getElementById('reportNonDevWorkType');
    const projectSelect = document.getElementById('reportNonDevWorkProject');
    const titleInput = document.getElementById('reportNonDevWorkTitle');
    const descInput = document.getElementById('reportNonDevWorkDescription');
    const saveBtn = document.getElementById('saveReportNonDevWorkBtn');

    const workType = workTypeSelect.value;
    const projectId = parseInt(projectSelect.value);
    const title = titleInput.value.trim();

    if (!projectId) {
      this.showToast('请选择项目', 'error');
      projectSelect.focus();
      return;
    }

    if (!title) {
      const titleText = workType === 'next_week_plan' ? '工作计划标题' : '工作说明标题';
      this.showToast(`请输入${titleText}`, 'error');
      titleInput.focus();
      return;
    }

    const data = {
      work_type: workType,
      title: title,
      description: descInput.value.trim() || null
    };

    // 如果是新建，添加项目和时间信息
    if (!this.isEditing) {
      data.project_id = projectId;
      data.report_period_start = this.reportStartDate;
      data.report_period_end = this.reportEndDate;
    }

    // 显示加载状态
    const originalText = saveBtn.textContent;
    saveBtn.textContent = '保存中...';
    saveBtn.disabled = true;

    try {
      let response;
      if (this.isEditing) {
        // 更新
        response = await fetch(`${this.apiBase}/non-dev-works/${this.editingId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`
          },
          body: JSON.stringify(data)
        });
      } else {
        // 创建
        response = await fetch(`${this.apiBase}/non-dev-works/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`
          },
          body: JSON.stringify(data)
        });
      }

      if (response.ok) {
        this.showToast(this.isEditing ? '更新成功' : '添加成功', 'success');
        this.hideForm();
        
        // 重新加载数据
        await this.loadNonDevWorks();
        
        // 通知父组件重新生成报告（报告重新生成时会包含最新的非开发工作数据）
        if (window.regenerateReportAfterNonDevWorkChange) {
          await window.regenerateReportAfterNonDevWorkChange();
        }
        
        // 重新渲染界面
        this.render();
        this.bindEvents();
      } else {
        const error = await response.json();
        this.showToast(error.message || '保存失败', 'error');
      }
    } catch (error) {
      console.error('Error saving non-dev work:', error);
      this.showToast('网络错误，请重试', 'error');
    } finally {
      saveBtn.textContent = originalText;
      saveBtn.disabled = false;
    }
  }

  /**
   * 编辑非开发工作
   */
  editNonDevWork(workId) {
    const work = this.nonDevWorks.find(w => w.id === workId);
    if (work) {
      this.showForm(work);
    }
  }

  /**
   * 删除非开发工作
   */
  async deleteNonDevWork(workId) {
    if (!confirm('确定要删除这条工作说明吗？')) {
      return;
    }

    try {
      const response = await fetch(`${this.apiBase}/non-dev-works/${workId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${this.token}` }
      });

      if (response.ok) {
        this.showToast('删除成功', 'success');
        
        // 重新加载数据
        await this.loadNonDevWorks();
        
        // 通知父组件重新生成报告（报告重新生成时会包含最新的非开发工作数据）
        if (window.regenerateReportAfterNonDevWorkChange) {
          await window.regenerateReportAfterNonDevWorkChange();
        }
        
        // 重新渲染界面
        this.render();
        this.bindEvents();
      } else {
        const error = await response.json();
        this.showToast(error.message || '删除失败', 'error');
      }
    } catch (error) {
      console.error('Error deleting non-dev work:', error);
      this.showToast('网络错误，请重试', 'error');
    }
  }

  /**
   * 获取非开发工作列表（供外部调用）
   */
  getNonDevWorks() {
    return this.nonDevWorks;
  }

  /**
   * HTML转义
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * 显示提示消息
   */
  showToast(message, type = 'info') {
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // 添加样式
    Object.assign(toast.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      padding: '12px 20px',
      borderRadius: '6px',
      color: 'white',
      fontWeight: '500',
      zIndex: '10000',
      opacity: '0',
      transform: 'translateY(-10px)',
      transition: 'all 0.3s ease'
    });

    // 根据类型设置背景色
    switch (type) {
      case 'success':
        toast.style.backgroundColor = '#10b981';
        break;
      case 'error':
        toast.style.backgroundColor = '#ef4444';
        break;
      default:
        toast.style.backgroundColor = '#3b82f6';
    }

    document.body.appendChild(toast);

    // 显示动画
    setTimeout(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    }, 10);

    // 自动移除
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 3000);
  }
}

// 导出到全局
window.ReportNonDevWorkManager = ReportNonDevWorkManager;