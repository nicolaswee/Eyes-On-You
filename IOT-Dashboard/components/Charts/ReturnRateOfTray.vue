<template>
  <div class="chart-box">
    <h2>Tray Return Rates Overtime</h2>
    <canvas ref="myChart" height="150px" width="600px"></canvas>
  </div>
</template>
<script>
import Chart from 'chart.js';
export default {
    props: ['trayReturnData'],
    methods: {
        trayReturnLabels(){
            return this.trayReturnData.value.map(item => new Date(item.ts).toString().substring(4,24))
        },
        trayReturnDataset(){
            return this.trayReturnData.value.map(item => item.value)
        },
    },
    mounted() {
      new Chart(this.$refs.myChart, {
        type: 'line',
        data: {
          labels: this.trayReturnLabels().slice(0,6),
          datasets: [
            {
              label: 'Tray Return Rates Overtime',
              data: this.trayReturnDataset().slice(0,6)
            }
          ]
        }
      });
  }
}
</script>
<style scoped>
.chart-box{
  width: 100%;
}
</style>