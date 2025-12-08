<template>
  <div id="app">
    <GanttChart />
  </div>
</template>

<script>
import GanttChart from './components/GanttChart.vue'

export default {
  name: 'App',
  components: {
    GanttChart
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', 'Microsoft YaHei', sans-serif;
  background-color: #f5f5f5;
}

#app {
  padding: 20px;
  min-height: 100vh;
}
</style>