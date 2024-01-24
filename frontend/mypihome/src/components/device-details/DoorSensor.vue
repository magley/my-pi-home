<script setup>
const props = defineProps({
    device: Object
});

const openString = (device) => {
    if (device['open'] === 1) {
        return "Open!";
    } else if (device['open'] === 0) {
        return "Closed";
    }
    return "?";
}

</script>

<template>
<img src="/ico_door_sensor.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
<span :class="{green: device['open']}">{{ openString(device) }}</span>
</template>