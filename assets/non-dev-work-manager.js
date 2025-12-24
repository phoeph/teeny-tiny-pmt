/**
 * 非开发工作管理组件
 * 用于在项目页面管理非开发工作说明
 */

class NonDevWorkManager {
  constructor(projectId, apiBase = 'http://localhost:8000/api') {
    this.projectId = projectId;
    this.apiBase = apiBase;
    this.token = localStorage.getItem('token');
    this.nonDevWorks = [];
    this.isEditing = false;
    this.editingId = null;
  }

  /**
   * 初始化组件
   */
  async init() {
    await this.loadNonDevWorks();
    this.render();
    this.bindEvents();
  }

  /**
   * 加载非开发工作列表
   */
  async loadNonDevWorks() {
    try {
      const response = await fetch(`${this.apiBase}/non-dev-works/project/${this.projectId}`, {
        headers: { Authorization: `Bearer ${this.token}` }
      });
      
      if (response.ok) {
        this.nonDevWorks = await response.json();
      } else {
        // 加载失败，使用空数组
        this.nonDevWorks = [];
      }
    } catch (error) {
      // 网络错误，使用空数组
      this.nonDevWorks = [];
    }
  }

  /**
   * 渲染组件
   */
  render() {
    const container = document.getElementById('nonDevWorkContainer');
    if (!container) return;

    const html = `
      <div class="non-dev-work-section">
        <div class="section-header">
          <h4 style="font-size: 16px; font-weight: 600; color: var(--text-main); margin: 0; padding-left: 12px; border-left: 4px solid var(--primary);">
            其他非开发工作说明
          </h4>
          <button class="primary-btn btn-sm" id="addNonDevWorkBtn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            添加说明
          </button>
        </div>
        
        <div class="non-dev-work-list" id="nonDevWorkList">
          ${this.renderNonDevWorkList()}
        </div>
        
        <div class="non-dev-work-form" id="nonDevWorkForm" style="display: none;">
          <div class="form-group">
            <label>工作说明标题</label>
            <input type="text" id="nonDevWorkTitle" placeholder="例如：预估新需求工时并和政企领导汇报进度" />
          </div>
          <div class="form-group">
            <label>详细描述（可选）</label>
            <textarea id="nonDevWorkDescription" rows="3" placeholder="详细描述工作内容..."></textarea>
          </div>
          <div class="form-actions">
            <button class="ghost-btn" id="cancelNonDevWorkBtn">取消</button>
            <button class="primary-btn" id="saveNonDevWorkBtn">保存</button>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  /**
   * 渲染非开发工作列表
   */
  renderNonDevWorkList() {
    if (this.nonDevWorks.length === 0) {
      return `
        <div class="empty-state" style="padding: 20px; text-align: center; color: var(--text-secondary);">
          <p>暂无非开发工作说明</p>
        </div>
      `;
    }

    return this.nonDevWorks.map((work, index) => `
      <div class="non-dev-work-item" data-id="${work.id}">
        <div class="work-item-header">
          <span class="work-item-index">${index + 1}.</span>
          <span class="work-item-title">${this.escapeHtml(work.title)}</span>
          <div class="work-item-actions">
            <button class="btn-icon edit-work-btn" data-id="${work.id}" title="编辑">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button class="btn-icon delete-work-btn" data-id="${work.id}" title="删除">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3,6 5,6 21,6"></polyline>
                <path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2v2"></path>
              </svg>
            </button>
          </div>
        </div>
        ${work.description ? `<div class="work-item-description">${this.escapeHtml(work.description)}</div>` : ''}
      </div>
    `).join('');
  }

  /**
   * 绑定事件
   */
  bindEvents() {
    // 添加按钮
    const addBtn = document.getElementById('addNonDevWorkBtn');
    if (addBtn) {
      addBtn.addEventListener('click', () => this.showForm());
    }

    // 取消按钮
    const cancelBtn = document.getElementById('cancelNonDevWorkBtn');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.hideForm());
    }

    // 保存按钮
    const saveBtn = document.getElementById('saveNonDevWorkBtn');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => this.saveNonDevWork());
    }

    // 编辑和删除按钮
    const container = document.getElementById('nonDevWorkList');
    if (container) {
      container.addEventListener('click', (e) => {
        const editBtn = e.target.closest('.edit-work-btn');
        const deleteBtn = e.target.closest('.delete-work-btn');

        if (editBtn) {
          const workId = parseInt(editBtn.dataset.id);
          this.editNonDevWork(workId);
        } else if (deleteBtn) {
          const workId = parseInt(deleteBtn.dataset.id);
          this.deleteNonDevWork(workId);
        }
      });
    }
  }

  /**
   * 显示表单
   */
  showForm(work = null) {
    this.isEditing = !!work;
    this.editingId = work ? work.id : null;

    const form = document.getElementById('nonDevWorkForm');
    const titleInput = document.getElementById('nonDevWorkTitle');
    const descInput = document.getElementById('nonDevWorkDescription');

    if (work) {
      titleInput.value = work.title;
      descInput.value = work.description || '';
    } else {
      titleInput.value = '';
      descInput.value = '';
    }

    form.style.display = 'block';
    titleInput.focus();
  }

  /**
   * 隐藏表单
   */
  hideForm() {
    const form = document.getElementById('nonDevWorkForm');
    form.style.display = 'none';
    this.isEditing = false;
    this.editingId = null;
  }

  /**
   * 保存非开发工作
   */
  async saveNonDevWork() {
    const titleInput = document.getElementById('nonDevWorkTitle');
    const descInput = document.getElementById('nonDevWorkDescription');
    const saveBtn = document.getElementById('saveNonDevWorkBtn');

    const title = titleInput.value.trim();
    if (!title) {
      this.showToast('请输入工作说明标题', 'error');
      titleInput.focus();
      return;
    }

    const data = {
      title: title,
      description: descInput.value.trim() || null
    };

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
          body: JSON.stringify({
            ...data,
            project_id: this.projectId
          })
        });
      }

      if (response.ok) {
        await this.loadNonDevWorks();
        this.render();
        this.bindEvents();
        this.hideForm();
        this.showToast(this.isEditing ? '更新成功' : '添加成功', 'success');
      } else {
        const error = await response.json();
        this.showToast(error.message || '保存失败', 'error');
      }
    } catch (error) {
      // 保存失败
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
        await this.loadNonDevWorks();
        this.render();
        this.bindEvents();
        this.showToast('删除成功', 'success');
      } else {
        const error = await response.json();
        this.showToast(error.message || '删除失败', 'error');
      }
    } catch (error) {
      // 删除失败
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
window.NonDevWorkManager = NonDevWorkManager;