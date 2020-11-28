<template>
    <div class="log-page">
        <h1>Table {{tableNumber}}</h1>
        <div class="cell-container">
            <div class="dashboard-cell">
                <div>
                    <span>Trays Detected</span>
                    <span>{{ratioPeopleData.total_trays}}</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Patrons Detected</span>
                    <span>{{ratioPeopleData.total_number_of_people}}</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Avg Time Spent</span>
                    <span>{{(ratioPeopleData.average_time_spent / 60000).toFixed(2)}} mins</span>
                </div>
            </div>
        </div>
        <div class="cell-container">
            <div class="dashboard-cell">
                <div>
                    <span>Table's Tray Return Rate</span>
                    <span>{{(ratioPeopleData.ratio_of_trays_return * 100).toFixed(0 )}}%</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Self Cleaning Patrons</span>
                    <span>{{ratioPeopleData.number_of_people_clear}}</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Avg Time Left Unclear</span>
                    <span>{{(tableTimeData.mean_time_not_clean / 60000).toFixed(2)}} mins</span>
                </div>
            </div>
        </div>
        <!-- <div class="chart-container">
            TODO
            <ReturnRateOfTrayForTable :tableTrayReturnData="tableTrayReturnData" :tableNumber="tableNumber"/>
        </div> -->
    </div>
</template>
<script>
import ReturnRateOfTrayForTable from './../Charts/ReturnRateOfTrayForTable.vue';

export default {
    components: { ReturnRateOfTrayForTable },
    data(){
        return {
            tableNumber: this.$route.query.table ? this.$route.query.table : 0,
            rpi_id: this.$route.query.rpi_id ? this.$route.query.rpi_id : 0,
            ratioPeopleData: {},
            tableTimeData: {},
            tableTrayReturnData: {
                "mean": 0.25,
                "status": true,
                "value": [
                    {
                        "ts": 1602401755088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602398155088,
                        "value": 0.3333333333333333
                    },
                    {
                        "ts": 1602394555088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602390955088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602387355088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602383755088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602380155088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602376555088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602372955088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602369355088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602365755088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602362155088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602358555088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602354955088,
                        "value": 0.0
                    },
                    {
                        "ts": 1602351355088,
                        "value": 0.0
                    }

                ]
            },
        }
    },
    async mounted(){
        try{
            let response1 = await fetch(`${process.env.BASEAPIURL}/ratio_of_people_table?rpi_id=${this.rpi_id}`)
                .then(response => response.json())
                .then(data => {
                    this.ratioPeopleData = data
                    //console.log(this.ratioPeopleData)
                })

            let response2 = await fetch(`${process.env.BASEAPIURL}/number_of_tables?rpi_id=${this.rpi_id}`)
                .then(response => response.json())
                .then(data => {
                    this.tableTimeData = data
                    console.log(this.tableTimeData)
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
</style>