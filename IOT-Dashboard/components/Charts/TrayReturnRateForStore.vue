<template>
  <div class="chart-box">
    <h2>Ratio of Trays Being Returned from Store {{storeNumber}}</h2>
    <canvas ref="myChart" height="150px" width="600px"></canvas>
  </div>
</template>
<script>
import Chart from 'chart.js';
export default {
    props: ['trayReturnDataStore', 'storeNumber'],
    methods: {
        trayReturnLabels(){
            return this.trayReturnDataStore.value.map(item => new Date(item.ts).toString().substring(4,24))
        },
        trayReturnDataset(){
            return this.trayReturnDataStore.value.map(item => item.value)
        },
    },
    mounted() {
      new Chart(this.$refs.myChart, {
        type: 'line',
        data: {
          labels: this.trayReturnLabels(),
          datasets: [
            {
              label: 'Ratio of Trays Being Returned to store ' + this.storeNumber ,
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