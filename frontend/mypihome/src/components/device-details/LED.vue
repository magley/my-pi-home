<script setup>
const props = defineProps({
    device: Object
});

const onString = (device) => {
    if (device['switch'] === 1) {
        return "On";
    } else if (device['switch'] === 0) {
        return "Off";
    }
    return "?";
}

</script>

<template>
<img v-if="device['switch'] === 1" src="/ico_led.png" width="100" height="100" />
<img v-if="device['switch'] === 0" src="/ico_led_off.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
<span :class="{green: device['switch']}">{{ onString(device) }}</span>
<br />
</template>