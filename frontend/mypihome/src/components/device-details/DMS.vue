<script setup>
const props = defineProps({
    device: Object,
    dms_last_4: String,
    cur_idx: Number,
});

const green = (idx) => {
    return props.cur_idx == idx;
}

</script>

<template>
<div>
    <img src="/ico_dms.png" width="100" height="100" />
    <br />
    <b class="green">{{ device.name }}</b>
    <br />
    Pushed:
    <span v-for="(key, idx) in dms_last_4" :class="{ greenSpan: green(idx)}">
        {{ key }}
    </span>
</div>
</template>

<style>
    .greenSpan {
        color: hsla(160, 100%, 37%, 1);
    }
</style>