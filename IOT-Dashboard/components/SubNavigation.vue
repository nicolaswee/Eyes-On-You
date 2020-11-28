<template>
    <div class="sub-navigation">
        <nuxt-link to="/" v-for="(link, index) in links" v-bind:key="index" v-bind:class="{ active: active == index}"><div>{{link.title}}</div></nuxt-link>
    </div>
</template>
<script>
export default {
    props: ['active'],
    data(){
        return {
            links: [
                { url: "/", title: "Dashboard"}, 
                { url: "/?page=tray", title: "Tray Return Logs"},
                { url: "/?page=store", title: "Store Specific Logs"},
                { url: "/?page=table", title: "Table Specific Logs"},
            ]
        }
    }
}
</script>
<style scoped>
.sub-navigation{
    padding: 15px 0 0 0;
    background-color: var(--color-main);
    border-right: 1px var(--color-border) solid;
}
.sub-navigation a{
    color: var(--color-border);
    text-decoration: none;
}
.sub-navigation div{
    color: var(--color-border);
    padding: 10px 15px;
    width: max-content;
    cursor: pointer;
    width: 100%;
    white-space: nowrap;
}
.sub-navigation a.active, .sub-navigation a.active div {
    color: var(--color-white);
    font-weight: bold;
}
.sub-navigation div:hover{
    background-color: var(--color-highlight);
}
</style>