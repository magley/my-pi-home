<script setup>
const props = defineProps({
    device: Object
});

const gyroscope_accelertion = (device) => {
    let acc_x = device["accel.x"];
    let acc_y = device["accel.y"];
    let acc_z = device["accel.z"];
    let acc = Math.sqrt(acc_x**2 + acc_y**2 + acc_z**2);
    return `${acc.toFixed(2)}`
}
const gyroscope_rotation = (device) => {
    let gyro_x = device["gyro.x"];
    let gyro_y = device["gyro.y"];
    let gyro_z = device["gyro.z"];
    let gyro = Math.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2);
    return `${acc.toFixed(2)}`
}

</script>

<template>
<img src="/ico_gyro.png" width="100" height="100" />
<br />
<b class="green">{{ device.name }}</b>
<br />
{{ device.name }}: {{ gyroscope_accelertion(device) }} m/s<sup>2</sup>;
<br />
({{ device['gyro.x'].toFixed(2) }}, {{ device['gyro.y'].toFixed(2) }},{{ device['gyro.z'].toFixed(2) }})
</template>