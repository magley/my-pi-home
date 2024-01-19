<script setup>
const props = defineProps({
    device: Object
});

const buzzString = (device) => {
    if (device['buzz'] === 1) {
        return "Buzzing";
    } else if (device['buzz'] === 0) {
        return "No buzz";
    }
    return "?";
}

</script>

<template>
<img src="/ico_buzzer.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
<span :class="{green: device['buzz']}">{{ buzzString(device) }}</span>
</template>