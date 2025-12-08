import Vue from 'vue'
import Vuex from 'vuex'
import moment from 'moment'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    // 甘特图数据
    tasks: [
      {
        id: 1,
        name: '客户调研',
        parentId: null,
        level: 1,
        startDate: '2023-01-01',
        endDate: '2023-03-31',
        color: '#87ceeb',
        assignee: '武清高俊喜',
        children: [
          {
            id: 11,
            name: '分层走访',
            parentId: 1,
            level: 2,
            startDate: '2023-01-01',
            endDate: '2023-01-31',
            color: '#87ceeb',
            assignee: '武清高俊喜'
          },
          {
            id: 12,
            name: '获取商机',
            parentId: 1,
            level: 2,
            startDate: '2023-02-01',
            endDate: '2023-02-28',
            color: '#87ceeb',
            assignee: '武清高俊喜'
          }
        ]
      },
      {
        id: 2,
        name: '孵育',
        parentId: null,
        level: 1,
        startDate: '2023-04-01',
        endDate: '2023-12-31',
        color: '#ff6b6b',
        assignee: '企要斯冰栋',
        children: [
          {
            id: 21,
            name: '制定方案',
            parentId: 2,
            level: 2,
            startDate: '2023-04-01',
            endDate: '2023-05-31',
            color: '#98d982',
            assignee: '企要斯冰栋'
          },
          {
            id: 22,
            name: '沟通交流',
            parentId: 2,
            level: 2,
            startDate: '2023-06-01',
            endDate: '2023-07-31',
            color: '#feca57',
            assignee: '企要斯冰栋'
          }
        ]
      },
      {
        id: 3,
        name: '转化',
        parentId: null,
        level: 1,
        startDate: '2023-08-01',
        endDate: '2024-12-31',
        color: '#48dbfb',
        assignee: '集团教科刘保伟',
        children: [
          {
            id: 31,
            name: '应标签约',
            parentId: 3,
            level: 2,
            startDate: '2023-08-01',
            endDate: '2023-10-31',
            color: '#ff9ff3',
            assignee: '集团教科刘保伟'
          },
          {
            id: 32,
            name: '建设交付',
            parentId: 3,
            level: 2,
            startDate: '2023-11-01',
            endDate: '2024-08-31',
            color: '#98d982',
            assignee: '集团教科刘保伟'
          },
          {
            id: 33,
            name: '工单起租',
            parentId: 3,
            level: 2,
            startDate: '2024-09-01',
            endDate: '2024-11-30',
            color: '#98d982',
            assignee: '集团教科刘保伟'
          },
          {
            id: 34,
            name: '计收回款',
            parentId: 3,
            level: 2,
            startDate: '2024-12-01',
            endDate: '2024-12-31',
            color: '#feca57',
            assignee: '武清高俊喜'
          }
        ]
      }
    ],
    // 时间范围
    startDate: '2023-01-01',
    endDate: '2024-12-31',
    // 时间粒度 (day, week, month, quarter, year)
    timeScale: 'month'
  },
  mutations: {
    UPDATE_TASK(state, { taskId, updates }) {
      const updateTask = (tasks) => {
        for (let task of tasks) {
          if (task.id === taskId) {
            Object.assign(task, updates)
            return true
          }
          if (task.children && updateTask(task.children)) {
            return true
          }
        }
        return false
      }
      updateTask(state.tasks)
    },
    ADD_TASK(state, task) {
      if (task.parentId) {
        const findParent = (tasks) => {
          for (let parentTask of tasks) {
            if (parentTask.id === task.parentId) {
              if (!parentTask.children) {
                parentTask.children = []
              }
              parentTask.children.push(task)
              return true
            }
            if (parentTask.children && findParent(parentTask.children)) {
              return true
            }
          }
          return false
        }
        findParent(state.tasks)
      } else {
        state.tasks.push(task)
      }
    },
    DELETE_TASK(state, taskId) {
      const deleteTask = (tasks) => {
        for (let i = 0; i < tasks.length; i++) {
          if (tasks[i].id === taskId) {
            tasks.splice(i, 1)
            return true
          }
          if (tasks[i].children && deleteTask(tasks[i].children)) {
            return true
          }
        }
        return false
      }
      deleteTask(state.tasks)
    }
  },
  actions: {
    updateTask({ commit }, payload) {
      commit('UPDATE_TASK', payload)
    },
    addTask({ commit }, task) {
      commit('ADD_TASK', task)
    },
    deleteTask({ commit }, taskId) {
      commit('DELETE_TASK', taskId)
    }
  },
  getters: {
    flatTasks(state) {
      const flatten = (tasks, result = []) => {
        for (let task of tasks) {
          result.push(task)
          if (task.children) {
            flatten(task.children, result)
          }
        }
        return result
      }
      return flatten(state.tasks)
    },
    timeColumns(state) {
      const start = moment(state.startDate)
      const end = moment(state.endDate)
      const columns = []
      
      if (state.timeScale === 'month') {
        let current = start.clone().startOf('month')
        while (current.isSameOrBefore(end, 'month')) {
          columns.push({
            date: current.format('YYYY-MM'),
            label: current.format('MM月'),
            year: current.format('YYYY'),
            start: current.clone(),
            end: current.clone().endOf('month')
          })
          current.add(1, 'month')
        }
      }
      
      return columns
    }
  }
})