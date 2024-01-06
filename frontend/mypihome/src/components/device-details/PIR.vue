<script setup>
const props = defineProps({
    device: Object
});

const motionString = (device) => {
    if (device['motion'] == true) {
        return "Motion detected!";
    } else if (device['motion'] == false) {
        return "No motion";
    }
    return "?";
}

</script>

<template>
<img src="/ico_pir.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />

<span :class="{green: device['motion']}">{{ motionString(device) }}</span>
</template>
