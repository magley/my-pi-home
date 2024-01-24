<script setup>
const props = defineProps({
    device: Object
});

</script>

<template>
<img src="/ico_uds.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
Distance: {{ device.distance_in_cm.toFixed(3) }}cm
</template>