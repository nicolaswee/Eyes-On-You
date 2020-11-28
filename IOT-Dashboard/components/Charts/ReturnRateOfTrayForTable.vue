<template>
  <div class="chart-box">
    <h2>Tray Return Rates Overtime For Table {{tableNumber}}</h2>
    <canvas ref="myChart" height="150px" width="600px"></canvas>
  </div>
</template>
<script>
import Chart from 'chart.js';
export default {
    props: ['tableTrayReturnData', 'tableNumber'],
    methods: {
        trayReturnLabels(){
            return this.tableTrayReturnData.value.map(item => new Date(item.ts).toString().substring(4,24))
        },
        trayReturnDataset(){
            return this.tableTrayReturnData.value.map(item => item.value)
        },
    },
    mounted() {
      new Chart(this.$refs.myChart, {
        type: 'line',
        data: {
          labels: this.trayReturnLabels(),
          datasets: [
            {
              label: 'Table Tray Return Rates For Table ' + this.tableNumber ,
              data: this.trayReturnDataset()
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