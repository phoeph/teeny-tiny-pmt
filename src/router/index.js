import Vue from 'vue'
import VueRouter from 'vue-router'
import GanttChart from '../views/GanttChart.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'GanttChart',
    component: GanttChart
  }
]

const router = new VueRouter({
  mode: 'hash',
  routes
})

export default router