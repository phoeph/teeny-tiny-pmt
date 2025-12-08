<template>
  <div class="gantt-chart">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>任务清单：2.4 执行管控 - "甘特图" 的应用案例</h1>
      <div class="header-logo">
        <span style="color: #e60012; font-weight: bold;">中国联通</span>
      </div>
    </div>

    <!-- 甘特图主体 -->
    <div class="gantt-container">
      <!-- 时间轴头部 -->
      <div class="gantt-header">
        <div class="task-list-header">任务列表</div>
        <div class="time-header">
          <div class="year-row">
            <div v-for="year in years" :key="year.year" class="year-cell" :style="{ width: year.width + 'px' }">
              {{ year.year }}年
            </div>
          </div>
          <div class="month-row">
            <div v-for="month in months" :key="month.key" class="month-cell">
              {{ month.label }}
            </div>
          </div>
        </div>
        <div class="assignee-header">负责人</div>
      </div>

      <!-- 甘特图内容 -->
      <div class="gantt-body">
        <div class="task-list">
          <div v-for="task in tasks" :key="task.id" class="task-group">
            <!-- 主任务 -->
            <div class="task-row parent-task" :style="{ backgroundColor: getCategoryColor(task.category) }">
              <div class="task-name">
                <div class="task-title">{{ task.name }}</div>
                <div class="task-category">{{ task.category }}</div>
              </div>
            </div>
            
            <!-- 子任务 -->
            <div v-for="subtask in task.subtasks" :key="subtask.id" class="task-row subtask">
              <div class="task-name">
                <div class="task-title">{{ subtask.name }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 时间轴内容 -->
        <div class="timeline">
          <div v-for="task in tasks" :key="task.id" class="task-group-timeline">
            <!-- 主任务时间条 -->
            <div class="task-row-timeline">
              <div 
                class="task-bar" 
                :style="getTaskBarStyle(task)"
                @click="editTask(task)"
                @mousedown="startDrag(task, $event)"
              >
                <div class="resize-handle left" @mousedown.stop="startResize(task, 'left', $event)"></div>
                <span class="task-bar-text">{{ task.description || task.name }}</span>
                <div class="resize-handle right" @mousedown.stop="startResize(task, 'right', $event)"></div>
              </div>
            </div>
            
            <!-- 子任务时间条 -->
            <div v-for="subtask in task.subtasks" :key="subtask.id" class="task-row-timeline">
              <div 
                class="task-bar" 
                :style="getTaskBarStyle(subtask)"
                @click="editTask(subtask)"
                @mousedown="startDrag(subtask, $event)"
              >
                <div class="resize-handle left" @mousedown.stop="startResize(subtask, 'left', $event)"></div>
                <span class="task-bar-text">{{ subtask.description || subtask.name }}</span>
                <div class="resize-handle right" @mousedown.stop="startResize(subtask, 'right', $event)"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 负责人列 -->
        <div class="assignee-list">
          <div v-for="task in tasks" :key="task.id" class="task-group-assignee">
            <div class="assignee-row">
              <div class="assignee-avatar">{{ getInitials(task.assignee) }}</div>
              <span class="assignee-name">{{ task.assignee }}</span>
            </div>
            <div v-for="subtask in task.subtasks" :key="subtask.id" class="assignee-row">
              <div class="assignee-avatar">{{ getInitials(subtask.assignee) }}</div>
              <span class="assignee-name">{{ subtask.assignee }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务编辑弹窗 -->
    <div v-if="showEditDialog" class="edit-dialog" @click.self="closeEditDialog">
      <div class="dialog-content">
        <h3>编辑任务</h3>
        <div class="form-group">
          <label>任务名称:</label>
          <input v-model="editingTask.name" type="text" />
        </div>
        <div class="form-group">
          <label>描述:</label>
          <input v-model="editingTask.description" type="text" />
        </div>
        <div class="form-group">
          <label>负责人:</label>
          <input v-model="editingTask.assignee" type="text" />
        </div>
        <div class="form-group">
          <label>颜色:</label>
          <input v-model="editingTask.color" type="color" />
        </div>
        <div class="form-actions">
          <button @click="saveTask" class="btn-primary">保存</button>
          <button @click="closeEditDialog" class="btn-secondary">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GanttChart',
  data() {
    return {
      columnWidth: 80,
      rowHeight: 50,
      showEditDialog: false,
      editingTask: null,
      dragInfo: null,
      resizeInfo: null,
      
      // 示例数据
      tasks: [
        {
          id: 1,
          name: '客户调研',
          category: '触达',
          startMonth: 0, // 相对于2023年1月的月份偏移
          duration: 3,
          color: '#87ceeb',
          assignee: '武清高俊喜',
          description: '特变电业二总部筹组配置',
          subtasks: [
            {
              id: 11,
              name: '分层走访',
              startMonth: 0,
              duration: 1,
              color: '#87ceeb',
              assignee: '武清高俊喜'
            },
            {
              id: 12,
              name: '获取商机',
              startMonth: 1,
              duration: 1,
              color: '#87ceeb',
              assignee: '武清高俊喜'
            }
          ]
        },
        {
          id: 2,
          name: '孵育',
          category: '孵育',
          startMonth: 3,
          duration: 6,
          color: '#ff6b6b',
          assignee: '企要斯冰栋',
          description: '撰写方案',
          subtasks: [
            {
              id: 21,
              name: '制定方案',
              startMonth: 3,
              duration: 2,
              color: '#98d982',
              assignee: '企要斯冰栋'
            },
            {
              id: 22,
              name: '沟通交流',
              startMonth: 5,
              duration: 3,
              color: '#feca57',
              assignee: '企要斯冰栋',
              description: '撰写招标文件多轮议价'
            }
          ]
        },
        {
          id: 3,
          name: '转化',
          category: '转化',
          startMonth: 7,
          duration: 17,
          color: '#48dbfb',
          assignee: '集团教科刘保伟',
          subtasks: [
            {
              id: 31,
              name: '应标签约',
              startMonth: 7,
              duration: 3,
              color: '#ff9ff3',
              assignee: '集团教科刘保伟',
              description: '应标签约'
            },
            {
              id: 32,
              name: '建设交付',
              startMonth: 10,
              duration: 10,
              color: '#98d982',
              assignee: '集团教科刘保伟',
              description: '项目总体建设完成 95%'
            },
            {
              id: 33,
              name: '工单起租',
              startMonth: 20,
              duration: 3,
              color: '#98d982',
              assignee: '集团教科刘保伟',
              description: '项目终验完成'
            },
            {
              id: 34,
              name: '计收回款',
              startMonth: 23,
              duration: 1,
              color: '#feca57',
              assignee: '武清高俊喜',
              description: '项目计收82%，项目回款43%'
            }
          ]
        }
      ],
      
      // 时间轴数据
      months: [
        // 2023年
        { key: '2023-Q1', label: 'Q1', year: 2023 },
        { key: '2023-Q2', label: 'Q2', year: 2023 },
        { key: '2023-Q3', label: 'Q3', year: 2023 },
        { key: '2023-Q4', label: 'Q4', year: 2023 },
        // 2024年
        { key: '2024-Q1', label: 'Q1', year: 2024 },
        { key: '2024-Q2', label: 'Q2', year: 2024 },
        { key: '2024-Q3', label: 'Q3', year: 2024 },
        { key: '2024-Q4', label: 'Q4', year: 2024 },
        // 2025年
        { key: '2025-1', label: '1月', year: 2025 },
        { key: '2025-2', label: '2月', year: 2025 },
        { key: '2025-3', label: '3月', year: 2025 },
        { key: '2025-4', label: '4月', year: 2025 },
        { key: '2025-5', label: '5月', year: 2025 },
        { key: '2025-6', label: '6月', year: 2025 },
        { key: '2025-7', label: '7月', year: 2025 },
        { key: '2025-8', label: '8月', year: 2025 },
        { key: '2025-9', label: '9月', year: 2025 },
        { key: '2025-10', label: '10月', year: 2025 },
        { key: '2025-11', label: '11月', year: 2025 },
        { key: '2025-12', label: '12月', year: 2025 }
      ]
    }
  },
  
  computed: {
    years() {
      const yearGroups = []
      let currentYear = null
      let count = 0
      
      this.months.forEach(month => {
        if (month.year !== currentYear) {
          if (currentYear !== null) {
            yearGroups.push({
              year: currentYear,
              width: count * this.columnWidth
            })
          }
          currentYear = month.year
          count = 1
        } else {
          count++
        }
      })
      
      if (currentYear !== null) {
        yearGroups.push({
          year: currentYear,
          width: count * this.columnWidth
        })
      }
      
      return yearGroups
    }
  },
  
  methods: {
    getCategoryColor(category) {
      const colors = {
        '触达': '#e6f7ff',
        '孵育': '#fff2e8', 
        '转化': '#f6ffed'
      }
      return colors[category] || '#f5f5f5'
    },
    
    getTaskBarStyle(task) {
      const left = task.startMonth * this.columnWidth
      const width = Math.max(task.duration * this.columnWidth, 60)
      
      return {
        left: left + 'px',
        width: width + 'px',
        backgroundColor: task.color,
        position: 'absolute',
        top: '8px',
        height: '34px',
        borderRadius: '4px',
        display: 'flex',
        alignItems: 'center',
        padding: '0 8px',
        color: 'white',
        fontSize: '12px',
        cursor: 'pointer',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }
    },
    
    getInitials(name) {
      if (!name) return 'NA'
      return name.length > 2 ? name.slice(-2) : name
    },
    
    editTask(task) {
      this.editingTask = { ...task }
      this.showEditDialog = true
    },
    
    closeEditDialog() {
      this.showEditDialog = false
      this.editingTask = null
    },
    
    saveTask() {
      if (this.editingTask) {
        // 更新原任务数据
        const updateTask = (tasks) => {
          for (let task of tasks) {
            if (task.id === this.editingTask.id) {
              Object.assign(task, this.editingTask)
              return true
            }
            if (task.subtasks && updateTask(task.subtasks)) {
              return true
            }
          }
        }
        updateTask(this.tasks)
      }
      this.closeEditDialog()
    },
    
    startDrag(task, event) {
      this.dragInfo = {
        task: task,
        startX: event.clientX,
        originalStartMonth: task.startMonth
      }
      
      document.addEventListener('mousemove', this.handleDrag)
      document.addEventListener('mouseup', this.endDrag)
      event.preventDefault()
    },
    
    handleDrag(event) {
      if (!this.dragInfo) return
      
      const deltaX = event.clientX - this.dragInfo.startX
      const monthDelta = Math.round(deltaX / this.columnWidth)
      const newStartMonth = Math.max(0, this.dragInfo.originalStartMonth + monthDelta)
      
      this.dragInfo.task.startMonth = newStartMonth
    },
    
    endDrag() {
      this.dragInfo = null
      document.removeEventListener('mousemove', this.handleDrag)
      document.removeEventListener('mouseup', this.endDrag)
    },
    
    startResize(task, direction, event) {
      this.resizeInfo = {
        task: task,
        direction: direction,
        startX: event.clientX,
        originalStartMonth: task.startMonth,
        originalDuration: task.duration
      }
      
      document.addEventListener('mousemove', this.handleResize)
      document.addEventListener('mouseup', this.endResize)
      event.preventDefault()
    },
    
    handleResize(event) {
      if (!this.resizeInfo) return
      
      const deltaX = event.clientX - this.resizeInfo.startX
      const monthDelta = Math.round(deltaX / this.columnWidth)
      
      if (this.resizeInfo.direction === 'left') {
        const newStartMonth = Math.max(0, this.resizeInfo.originalStartMonth + monthDelta)
        const newDuration = this.resizeInfo.originalDuration - (newStartMonth - this.resizeInfo.originalStartMonth)
        if (newDuration > 0) {
          this.resizeInfo.task.startMonth = newStartMonth
          this.resizeInfo.task.duration = newDuration
        }
      } else {
        const newDuration = Math.max(1, this.resizeInfo.originalDuration + monthDelta)
        this.resizeInfo.task.duration = newDuration
      }
    },
    
    endResize() {
      this.resizeInfo = null
      document.removeEventListener('mousemove', this.handleResize)
      document.removeEventListener('mouseup', this.endResize)
    }
  }
}
</script>

<style scoped>
.gantt-chart {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.gantt-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  overflow: hidden;
}

.gantt-header {
  display: flex;
  background: #f8f9fa;
  border-bottom: 2px solid #e4e7ed;
}

.task-list-header {
  width: 250px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: #e60012;
  color: white;
  border-right: 1px solid #e4e7ed;
}

.time-header {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.year-row, .month-row {
  display: flex;
  height: 40px;
}

.year-cell, .month-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #e4e7ed;
  font-weight: 600;
  width: 80px;
}

.year-cell {
  background: #f0f2f5;
  color: #e60012;
  font-size: 14px;
}

.month-cell {
  background: #f8f9fa;
  color: #606266;
  font-size: 12px;
}

.assignee-header {
  width: 150px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: #e60012;
  color: white;
  border-left: 1px solid #e4e7ed;
}

.gantt-body {
  display: flex;
}

.task-list {
  width: 250px;
  background: #fafafa;
}

.timeline {
  flex: 1;
  position: relative;
  background: white;
}

.assignee-list {
  width: 150px;
  background: #fafafa;
  border-left: 1px solid #e4e7ed;
}

.task-group, .task-group-timeline, .task-group-assignee {
  border-bottom: 1px solid #f0f0f0;
}

.task-row {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.task-row:hover {
  background-color: rgba(0,0,0,0.02) !important;
}

.parent-task {
  font-weight: 600;
}

.subtask {
  padding-left: 32px;
  font-size: 14px;
}

.task-name {
  flex: 1;
}

.task-title {
  color: #303133;
  line-height: 1.4;
}

.task-category {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
  padding: 2px 6px;
  background: #f0f2f5;
  border-radius: 3px;
  display: inline-block;
  width: fit-content;
}

.task-row-timeline {
  height: 50px;
  position: relative;
  border-bottom: 1px solid #f0f0f0;
}

.task-bar {
  position: relative;
  user-select: none;
  transition: all 0.2s ease;
}

.task-bar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

.task-bar-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.resize-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: ew-resize;
  background: rgba(255,255,255,0.3);
  opacity: 0;
  transition: opacity 0.2s;
}

.resize-handle.left {
  left: 0;
  border-radius: 4px 0 0 4px;
}

.resize-handle.right {
  right: 0;
  border-radius: 0 4px 4px 0;
}

.task-bar:hover .resize-handle {
  opacity: 1;
}

.assignee-row {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
}

.assignee-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  margin-right: 8px;
  flex-shrink: 0;
}

.assignee-name {
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 编辑弹窗样式 */
.edit-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  width: 400px;
  max-width: 90vw;
}

.dialog-content h3 {
  margin-bottom: 20px;
  color: #303133;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #409eff;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover {
  background: #337ab7;
}

.btn-secondary {
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-secondary:hover {
  background: #ecf5ff;
}
</style>