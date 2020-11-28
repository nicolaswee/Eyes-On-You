<template>
    <div class="side-navigation">
        <User />
        <User />
        <User />
    </div>
</template>
<script>
import User from './Navigation/User.vue';

export default {
    components: { User }
}
</script>
<style scoped>
.side-navigation{
    position: sticky;
    top: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 15px;
}
</style>