<script setup>
const props = defineProps({
    device: Object
});

</script>

<template>
<img src="/ico_dms.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
Pushed:
<br/>
<span class="green">{{ device['keys'] }}</span>
</template>