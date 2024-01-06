<script setup>
import DHT from '@/components/device-details/DHT.vue';
import Gyro from '@/components/device-details/Gyro.vue';
import UDS from '@/components/device-details/UDS.vue';
import PIR from '@/components/device-details/PIR.vue';

const props = defineProps({
    device: Object
});



</script>

<template>

<template v-if="device.temperature != undefined">
    <DHT :device="device" />
</template>

<template v-else-if="device['accel.x'] != undefined">
    <Gyro :device="device" />
</template>

<template v-else-if="device.distance_in_cm != undefined">
    <UDS :device="device" />
</template>

<template v-else-if="device.motion != undefined">
    <PIR :device="device" />
</template>

<!-- Else-->
<template v-else>
    {{ device }}
</template>

</template>