<template>
    <div class="chart-box">
        <h2>Number of Trays Return at Return Point {{returnNumber}}</h2>
        <canvas ref="myChart" height="150px" width="600px"></canvas>
    </div>
</template>
<script>
export default {
props: ['trayReturnStationData', 'returnNumber'],
    methods: {
        trayReturnLabels(){
            return this.trayReturnStationData.value.map(item => new Date(item.ts).toString().substring(4,24))
        },
        trayReturnDataset(){
            return this.trayReturnStationData.value.map(item => item.value)
        },
    },
    mounted() {
        new Chart(this.$refs.myChart, {
            type: 'bar',
            data: {
                labels: this.trayReturnLabels(),
                datasets: [
                    {
                        label: 'Number of Tray Return',
                        data: this.trayReturnDataset(),
                    }
                ]
            }
        });
  }
}
</script>