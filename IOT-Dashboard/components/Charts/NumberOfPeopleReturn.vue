<template>
    <div>
        <h2>Group Size Most Likely to Return Trays</h2>
        <canvas ref="myChart" height="100px"></canvas>
    </div>
</template>
<script>
export default {
    props: ['numberOfPeopleReturnData'],
    methods: {
        numberReturnLabels(){
            return this.numberOfPeopleReturnData.groups_clear.map(item => item.size + ' Person')
        },
        numberReturnDataset(){
            return this.numberOfPeopleReturnData.groups_clear.map(item => item.value)
        },
    },
    mounted() {
        new Chart(this.$refs.myChart, {
            type: 'doughnut',
            data: {
                labels: this.numberReturnLabels(),
                datasets: [
                    {
                        data: this.numberReturnDataset(),
                        backgroundColor: ['#EAA7B6','#FFE88A','#A1E3BA','#A0B2E4']
                    }
                ]
            }
        });
  }
}
</script>
<style scoped>

</style>