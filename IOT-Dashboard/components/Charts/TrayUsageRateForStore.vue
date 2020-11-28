<template>
  <div class="chart-box">
    <h2>Usage of Trays from store {{storeNumber}}</h2>
    <canvas ref="myChart" height="150px" width="600px"></canvas>
  </div>
</template>
<script>
import Chart from 'chart.js';
export default {
    props: ['trayUseDataStore', 'storeNumber'],
    methods: {
        trayUsageLabels(){
            return this.trayUseDataStore.value.map(item => new Date(item.ts).toString().substring(4,24))
        },
        trayUsageDataset(){
            return this.trayUseDataStore.value.map(item => item.value)
        },
    },
    mounted() {
      new Chart(this.$refs.myChart, {
        type: 'bar',
        data: {
          labels: this.trayUsageLabels(),
          datasets: [
            {
              label: 'Usage of Trays from store ' + this.storeNumber ,
              data: this.trayUsageDataset()
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