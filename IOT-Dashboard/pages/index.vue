<template>
  <div class="container" v-if="allLoaded">
    <SideNavigation />
    <SubNavigation :active="currentTab" />
    <Dashboard v-if="$route.query.page == '' || !$route.query.page" 
        :trayReturnData="trayReturnData"
        :numberOfPeopleReturnData="numberOfPeopleReturnData"
        :trayLeaveStoreData="trayLeaveStoreData"
        :trayAverageRate="trayAverageRate"
        :trayReturnDataStore="trayReturnDataStore"
    />
    <TrayDashboard v-else-if="$route.query.page == 'tray'" :trayReturnData="trayReturnData" />
    <TableDashboard v-else-if="$route.query.page == 'table'" :trayReturnData="trayReturnData" />
    <StoreDashboard v-else-if="$route.query.page == 'store'" 
        :trayLeaveStoreData="trayLeaveStoreData"
        :trayAverageRate="trayAverageRate"
        :trayReturnDataStore="trayReturnDataStore"
        :trayUseDataStore="trayUseDataStore"
    />
  </div>
</template>
<script>
import SideNavigation from './../components/SideNavigation.vue';
import SubNavigation from './../components/SubNavigation.vue';
import Dashboard from './../components/LogPage/Dashboard.vue';
import TrayDashboard from './../components/LogPage/TrayDashboard.vue';
import TableDashboard from './../components/LogPage/TableDashboard.vue';
import StoreDashboard from './../components/LogPage/StoreDashboard.vue';

export default {
  components: { SideNavigation, SubNavigation, Dashboard, TrayDashboard, TableDashboard, StoreDashboard },
  computed:{
      currentTab(){
          if(this.$route.query.page == '' || !this.$route.query.page) return 0
          if(this.$route.query.page == 'tray') return 1
          if(this.$route.query.page == 'store') return 2
          if(this.$route.query.page == 'table') return 3
      },
      allLoaded(){
          return this.r1Loaded && this.r2Loaded && this.r3Loaded && this.r4Loaded && this.r5Loaded && this.r6Loaded
      }
  },
  data(){
    return {
        r1Loaded: false,
        r2Loaded: false,
        r3Loaded: false,
        r4Loaded: false,
        r5Loaded: false,
        r6Loaded: false,
        numberOfPeopleReturnData: {},
        trayReturnData: {},
        trayLeaveStoreData: {},
        trayAverageRate : 0,
        trayReturnDataStore: {},
        trayUseDataStore: {}
    }
  },
  async created(){
      try {
          let response1 = await fetch(process.env.BASEAPIURL +'/ratio_of_people')
            .then(response=>response.json())
            .then(data => {
                this.numberOfPeopleReturnData = data
                this.r1Loaded = true;
                // console.log(this.numberOfPeopleReturnData)
            })

            let response2 = await fetch(process.env.BASEAPIURL +'/ratio_of_trays')
                .then(response=>response.json())
                .then(data => {
                    this.trayReturnData = data
                    this.r2Loaded = true;
                    //console.log(this.trayReturnData)
                })
            let response3 = await fetch(process.env.BASEAPIURL +'/total_number_trays_leave_store')
                .then(response=>response.json())
                .then(data => {
                    this.trayLeaveStoreData = data
                    this.r3Loaded = true;
                    // console.log(this.trayLeaveStoreData)
                })
            let response4 = await fetch(process.env.BASEAPIURL +'/tray_average_rate')
                .then(response => response.json())
                .then(data => {
                    this.trayAverageRate = (data.result / 60000).toFixed(2)
                    this.r4Loaded = true;
                    // console.log(this.trayAverageRate)
                })
            let response5 = await fetch(process.env.BASEAPIURL +'/ratio_of_trays_store?store_id=1')
                .then(response => response.json())
                .then(data => {
                    this.trayReturnDataStore = data
                    this.r5Loaded = true;
                    // console.log(this.trayReturnDataStore)
                })

            // For Number of trays used
            let response6 = await fetch(process.env.BASEAPIURL +'/timeseries_tray_out')
                .then(response => response.json())
                .then(data => {
                    this.trayUseDataStore = data
                    this.r6Loaded = true;
                    //console.log(this.trayUseDataStore)
                })
      } catch (error){

      }
  }
}
</script>
<style>
.container {
  margin: 0;
  min-height: 100vh;
  width: 100%;
  display:flex;
}

</style>
