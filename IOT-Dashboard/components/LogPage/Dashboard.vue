<template>
    <div class="log-page">
        <h1>Dashboard</h1>
        <div class="chart-container">
            <ReturnRateOfTray :trayReturnData="trayReturnData" />
        </div>
        <div class="cell-container">
            <div class="dashboard-cell">
                <div>
                    <span>Average Tray Return Rate</span>
                    <span>{{(trayReturnData.mean * 100).toFixed(0)}}%</span>
                </div>
            </div>
            <div class="dashboard-cell">
                <div>
                    <span>Ratio of People Returning Trays</span>
                    <span>{{(numberOfPeopleReturnData.mean * 100).toFixed(0)}}%<br>
                    {{numberOfPeopleReturnData.number_of_people_clear}} out of {{numberOfPeopleReturnData.total_number_of_people}} people</span>
                </div>
            </div>
            <div class="chart-container">
                <NumberOfPeopleReturn :numberOfPeopleReturnData="numberOfPeopleReturnData"/>
            </div>
        </div>
        <div class="cell-container">
            <div class="layout-container">
                <h2>Floor Overview</h2>
                <div class="layout-row">
                    <div class="layout-frame">
                        <img src="hawkerlayout.png" />

                        <nuxt-link to="/?page=table&table=193&rpi_id=2">
                            <div id="table-1" v-on:mouseover="showTable1Hover = true" v-on:mouseout="showTable1Hover = false">
                                <div v-if="showTable1Hover" id="table-1-hover">
                                    Table 193<br>
                                    <hr>
                                    Avg Time Left Unclear: {{(tableTimeData193.mean_time_not_clean / 60000).toFixed(2)}} mins
                                </div>
                            </div>
                        </nuxt-link>

                        <nuxt-link to="/?page=table&table=183&rpi_id=3">
                            <div id="table-2" v-on:mouseover="showTable2Hover = true" v-on:mouseout="showTable2Hover = false">
                                <div v-if="showTable2Hover" id="table-2-hover">
                                    Table 183<br>
                                    <hr>
                                    Avg Time Left Unclear: {{(tableTimeData183.mean_time_not_clean / 60000).toFixed(2)}} mins
                                </div>
                            </div>
                        </nuxt-link>
                        
                        <nuxt-link to="/?page=store&store=1">
                            <div id="store-1" v-on:mouseover="showStore1Hover = true" v-on:mouseout="showStore1Hover = false"></div>
                            <div v-if="showStore1Hover" id="store-1-hover">
                                <h3>Store 1</h3>
                                <hr>
                                Trays Used: {{trayLeaveStoreData["Trays used"]}}<br>
                                Avg Tray Return Time: {{trayAverageRate}} mins<br>
                                Return Ratio: {{(trayReturnDataStore.mean * 100).toFixed(0)}}%
                            </div>
                        </nuxt-link>

                        <nuxt-link to="/?page=tray&return=4">
                            <div id="return-1" v-on:mouseover="showReturn1Hover = true" v-on:mouseout="showReturn1Hover = false"></div>
                            <div v-if="showReturn1Hover" id="return-1-hover">
                                Tray Return 4<br>
                                <hr>    
                                <span>{{trayReturnStationData4.number_of_trays}}</span>
                            </div>
                        </nuxt-link>

                        <nuxt-link to="/?page=tray&return=5">
                            <div id="return-2" v-on:mouseover="showReturn2Hover = true" v-on:mouseout="showReturn2Hover = false"></div>
                            <div v-if="showReturn2Hover" id="return-2-hover">
                                Tray Return 5<br>
                                <hr>    
                                <span>{{trayReturnStationData5.number_of_trays}}</span>
                            </div>
                        </nuxt-link>
                    </div>
                    <div class="layout-details">
                    </div>
                </div>
            </div>
            
            <!-- map view ratio of people that clean up at a table Today view table hover-->
            <!-- ratio of people returning tray with regard to distance, hover over tray return -->
            <!-- ratio of trays return per store, hover over store -->
            <!-- group size more liekly to clean up put this at right side mini column -->
        </div>
    </div>
</template>
<script>
import ReturnRateOfTray from './../Charts/ReturnRateOfTray.vue';
import NumberOfPeopleReturn from './../Charts/NumberOfPeopleReturn.vue';

export default {
    props: ["trayReturnData", "numberOfPeopleReturnData", "trayLeaveStoreData", "trayAverageRate", "trayReturnDataStore"],
    components: { ReturnRateOfTray, NumberOfPeopleReturn },
    data(){
        return {
            showTable1Hover: false,
            showTable2Hover: false,
            showStore1Hover: false,
            showReturn1Hover: false,
            showReturn2Hover: false,
            trayReturnStationData4: {},
            trayReturnStationData5: {},
            tableTimeData183: {},
            tableTimeData193: {}
        }
    },
    async mounted(){  
        // get table 183
        let response183 = await fetch(`${process.env.BASEAPIURL}/number_of_tables?rpi_id=3`)
            .then(response => response.json())
            .then(data => {
                this.tableTimeData183 = data
            })
        // get table 193
        let response193 = await fetch(`${process.env.BASEAPIURL}/number_of_tables?rpi_id=2`)
            .then(response => response.json())
            .then(data => {
                this.tableTimeData193 = data
            })
    }
}
</script>
<style scoped>

.cell-container{
    display: flex;
}
.dashboard-cell{
    background-color: var(--color-white);
    border-radius: 25px;
    color: var(--color-highlight);
    width: min-content;
    margin-right: 20px;
    margin-bottom: 25px;
    height: auto;
    display: flex;
    align-items: flex-start;
}
.dashboard-cell div {
    display: flex;
    flex-direction: column;
    padding: 25px;
}
.dashboard-cell div > span:first-child{
    font-size: 1.5rem;
    font-weight: bold;
    width: 200px;
    text-align: center;
}
.dashboard-cell div > span:last-child{
    align-self: center;
    font-size: 1.4rem;
    padding-top: 25px;
    font-weight: normal;
    text-align: center;
}

h1, h2{
    margin-bottom: 15px;
}

/* MAP LAYOUT CSS */
.layout-container{
    background-color: white;
    padding: 25px;
    width: min-content;
    border-radius: 25px;
    color: var(--color-highlight);
    display: flex;
    flex-direction: column;
}
.layout-row{
    display: flex;
}
.layout-frame{
    position: relative;
}
#table-1{
    position: absolute;
    top: 417px;
    left: 450px;
    height: 50px;
    width: 35px;
    background-color: var(--color-success);
}
#table-1-hover{
    position: absolute;
    top: -130px;
    left: -100px;
    background-color: var(--color-white);
    padding: 25px;
    border-radius: 25px;
    z-index: 2;
    width: 300px;
}
#table-2{
    position: absolute;
    top: 475px;
    left: 30px;
    height: 35px;
    width: 45px;
    background-color: var(--color-success);
}
#table-2-hover{
    position: absolute;
    top: -130px;
    left: 0px;
    background-color: var(--color-white);
    padding: 25px;
    border-radius: 25px;
    z-index: 2;
    width: 300px;
}

#store-1{
    position: absolute;
    top: 600px;
    left: 379px;
    height: 100px;
    width: 135px;
    background-color: var(--color-yellow);
}

#store-1-hover{
    position: absolute;
    top: 430px;
    left: 325px;
    background-color: var(--color-white);
    padding: 25px;
    width: 250px;
    border-radius: 25px;
    z-index: 2;
}

#return-1{
    position: absolute;
    top: 359px;
    left: 514px;
    height: 25px;
    width: 50px;
    background-color: var(--color-highlight);
}
#return-1-hover{
    position: absolute;
    top: 270px;
    left: 455px;
    background-color: var(--color-white);
    padding: 25px;
    border-radius: 25px;
    z-index: 2;
    width: 200px;
}
#return-2{
    position: absolute;
    top: 52px;
    left: 39px;
    height: 50px;
    width: 25px;
    background-color: var(--color-highlight);
}
#return-2-hover{
    position: absolute;
    top: 30px;
    left: 75px;
    background-color: var(--color-white);
    padding: 25px;
    border-radius: 25px;
    z-index: 2;
    width: 200px;
}
#store-1:hover, #return-2:hover, #return-1:hover{
    filter: brightness(0.7);
}
</style>