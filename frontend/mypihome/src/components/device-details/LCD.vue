<script setup>
const props = defineProps({
    device: Object
});

const lcdString = (device) => {
    let s = device['lcd'];
    s = s.replace("\n", "<br />");
    return s;
}

</script>

<template>
<img src="/ico_lcd.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
Text:<br/>
<span class="green" v-html="lcdString(device)"></span>
</template>