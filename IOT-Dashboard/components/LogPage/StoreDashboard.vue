<template>
    <div class="log-page">
        <h1>Store {{storeNumber}}</h1>
        <div class="cell-container">
            <div class="dashboard-cell">
                <div>
                    <span>Trays Currently Used</span>
                    <span>{{trayLeaveStoreData["Trays used"]}}</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Tray Avg Return Time</span>
                    <span>{{trayAverageRate}} mins</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Return Ratio</span>
                    <span>{{(trayReturnDataStore.mean * 100).toFixed(0)}}%</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Total Trays Used</span>
                    <span>{{trayLeaveStoreData["Trays returned"]}}</span>
                </div>
            </div>
        </div>
        <div class="chart-container">
            <TrayUsageRateForStore :trayUseDataStore="trayUseDataStore" :storeNumber="storeNumber" /> 
        </div>
        <div class="chart-container">
            <TrayReturnRateForStore :storeNumber="storeNumber" :trayReturnDataStore="trayReturnDataStore" />
        </div>
        <div class="layout-container">
            <div id="return-point-4">{{return4Count}} Shop Trays Returned Here</div>
            <div id="return-point-5">{{return5Count}} Shop Trays Returned Here</div>
            <img src="storetoreturnpoint.png"/>
        </div>
    </div>
</template>
<script>
import TrayReturnRateForStore from './../Charts/TrayReturnRateForStore.vue';
import TrayUsageRateForStore from './../Charts/TrayUsageRateForStore.vue';

export default {
    components: {TrayReturnRateForStore, TrayUsageRateForStore},
    props: ['trayLeaveStoreData', 'trayAverageRate', 'trayReturnDataStore' , 'trayUseDataStore'],
    data(){
        return {
            storeNumber: this.$route.query.store ? this.$route.query.store : 0,
            return4Count: 0,
            return5Count: 0,
        }
    },
    async mounted(){
        try {
            let response = fetch(process.env.BASEAPIURL + '/store_tray_returned')
                .then(response => response.json())
                .then(data => {
                    for( const index in data.result){
                        if (data.result[index].rpi_id == 4){
                            this.return4Count =  data.result[index].number_of_trays;
                        }
                        if (data.result[index].rpi_id == 5){
                            this.return5Count =  data.result[index].number_of_trays;
                        }
                    }
                })
        } catch (error) {

        }
    }
}
</script>
<style scoped>
.cell-container{
    margin: 25px 0px;
    display: flex;
    justify-content: space-between;
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
.layout-container{
    background-color: white;
    padding: 25px;
    width: min-content;
    border-radius: 25px;
    color: var(--color-highlight);
    position: relative;
}
#return-point-4, #return-point-5{
    position: absolute;
    background-color: white;
    padding: 25px;
    border-radius: 25px;
    border: var(--color-border) 2px solid;
}

#return-point-4{
    top:300px;
    left: 440px;
}
#return-point-5{
    top: 65px;
    left: 100px;
}
</style>