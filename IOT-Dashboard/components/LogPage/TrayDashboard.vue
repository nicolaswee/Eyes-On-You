<template>
    <div class="log-page">
      <h1>Tray Return Station {{returnNumber}}</h1>
      <div class="cell-container">
            <div class="dashboard-cell">
                <div>
                    <span>Trays Returned Here</span>
                    <span>{{trayReturnStationData.number_of_trays}}</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Avg Tray Time at Station</span>
                    <span>{{(trayReturnStationTimeData.ratio_of_trays_distance / 60000).toFixed(2)}} mins</span>
                </div>
            </div>
        </div>
        <div class="chart-container">
            <TrayReturnStationReturnRate 
                v-if="dataloaded"
                :returnNumber="returnNumber" 
                :trayReturnStationData="trayReturnStationData"/>
        </div>
    </div>
</template>
<script>
import TrayReturnStationReturnRate from './../Charts/TrayReturnStationReturnRate.vue';

export default {
    components: { TrayReturnStationReturnRate },
    props: [],
    data(){
        return {
            returnNumber: this.$route.query.return ? this.$route.query.return : 0,
            trayReturnStationData: {},
            trayReturnStationTimeData: {},
            dataloaded: false
        }
    },
    async mounted(){
        try{
            let response1 = await fetch(`${process.env.BASEAPIURL}/number_of_trays?rpi_id=${this.returnNumber}`)
                .then(response => response.json())
                .then(data => {
                    this.trayReturnStationData = data
                    this.dataloaded = true;
                    //console.log(this.trayReturnStationData)
                })
            let response2 = await fetch(`${process.env.BASEAPIURL}/ratio_of_trays_distance?rpi_id=1`)
                //fetch(`http://13.212.141.106/number_of_trays?rpi_id=${this.returnNumber}`)
                .then(response => response.json())
                .then(data => {
                    this.trayReturnStationTimeData = data
                    console.log(this.trayReturnStationTimeData)
                })
        } catch(error){

        }
    }
}
</script>
<style scoped>
.cell-container{
    margin: 25px 0px;
    display: flex;
    justify-content: flex-start;
    width: 100%;
}
.dashboard-cell{
    background-color: var(--color-white);
    border-radius: 25px;
    color: var(--color-highlight);
    width: 330px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 25px;
}
.dashboard-cell div {
    display: flex;
    padding: 25px;
    flex-direction: column;
}
.dashboard-cell div > span:first-child{
    font-size: 1.5rem;
    font-weight: bold;
    width: 100%;
    max-width: 330px;
}
.dashboard-cell div > span:last-child{
    align-self: center;
    font-size: 1.3rem;
    font-weight: normal;
    padding-top: 10px;
}
</style>