<script setup>
const props = defineProps({
    device: Object
});

const timeString = (device) => {
    let s = device['d4s7'];
    s = s.replace("\n", "<br />");
    // Don't display seconds
    s = s.substring(0, s.length - 3);
    return s;
}

</script>

<template>
<img src="/ico_d4s7.png" width="100" height="100" style="object-fit: contain;"/>
<br />
<b class="green">{{ device.name }}</b>
<br />
<span v-html="timeString(device)"></span>
</template>