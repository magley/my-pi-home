<script setup>
const props = defineProps({
    device: Object
});

</script>

<template>
<img src="/ico_dht.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
{{ device.temperature }}&deg;C, {{ device.humidity }}%
</template>