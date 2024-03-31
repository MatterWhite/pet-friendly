
<script setup>
import Header from "./Header.vue";
import WalkRequest from "./WalkRequest.vue";
import NewWalkRequestDialog from "./NewWalkRequestDialog.vue";
</script>


<script>
export default {
    data() {
        return {
            user: {}
        }
    },
    methods: {
    },
    mounted() {
        console.log('mounted')
    }
}
</script>

<template>
    <div class="root">
    </div>
</template>



<style scoped>
.root {
    height: 100vh;
    
    display: flex;
    flex-direction: column;
    flex-flow: column;
}
</style>