<script setup>
import DHT from '@/components/device-details/DHT.vue';
import Gyro from '@/components/device-details/Gyro.vue';
import UDS from '@/components/device-details/UDS.vue';
import PIR from '@/components/device-details/PIR.vue';
import DoorSensor from '@/components/device-details/DoorSensor.vue';
import DMS from '@/components/device-details/DMS.vue';
import Buzzer from '@/components/device-details/Buzzer.vue';
import LED from '@/components/device-details/LED.vue';
import LCD from '@/components/device-details/LCD.vue';
import D4S7 from './device-details/D4S7.vue';
import RGB from './device-details/RGB.vue';


const props = defineProps({
    device: Object,
    homeState: Object
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

<template v-else-if="device.open != undefined">
    <DoorSensor :device="device" />
</template>

<template v-else-if="device.keys != undefined">
    <DMS :device="device" :dms_last_4="String(homeState.dms_last_4)" :cur_idx="homeState.dms_cur_idx" />
</template>

<template v-else-if="device.buzz != undefined">
    <Buzzer :device="device" />
</template>

<template v-else-if="device.switch != undefined">
    <LED :device="device" />
</template>

<template v-else-if="device.lcd != undefined">
    <LCD :device="device" />
</template>

<template v-else-if="device.d4s7 != undefined">
    <D4S7 :device="device" />
</template>

<template v-else-if="device.rgb != undefined">
    <RGB :device="device" />
</template>

<!-- Else-->
<template v-else>
    {{ device }}
</template>

</template>