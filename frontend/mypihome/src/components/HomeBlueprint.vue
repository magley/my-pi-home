<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import HomeDeviceSvgElement from './HomeDeviceSvgElement.vue';
import HomeDeviceDetals from './HomeDeviceDetails.vue';

const homeState = ref(0);

let socket;
onMounted(() => {
    socket = new WebSocket("ws://127.0.0.1:5000/ws/state");
    socket.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        onHomeStateUpdate(msg);
    };
    socket.onerror = function(error) {
        console.error(error);
    };
});
onUnmounted(() => {
    socket.close();
});

const onHomeStateUpdate = (data) => {
    homeState.value = data;
}

const hoveredDevices = ref([]);
const onHoverDevice = (deviceCode) => {
    hoveredDevices.value.push(deviceCode);
}
const onUnhoverDevice = (deviceCode) => {
    hoveredDevices.value = hoveredDevices.value.filter((item) => item !== deviceCode);
}
const isHovered = (code) => {
    return hoveredDevices.value.filter((item) => item === code).length > 0;
}

</script>

<template>
    <h2>
        Number of people: {{homeState.number_of_people}}
    </h2> 
<div class="container">
    <svg class="left" width="800" height="800" xmlns="http://www.w3.org/2000/svg">
        <image href="../../public/home.png" />

        <!-- PI1 -->
        <HomeDeviceSvgElement label-text="RPIR2" :x= "95" :y="305" :ldx="-20" :ldy="-15" color="red" @mouseover="onHoverDevice('RPIR2')" @mouseleave="onUnhoverDevice('RPIR2')" :force-hover="isHovered('RPIR2')"/>
        <HomeDeviceSvgElement label-text="DMS"   :x="190" :y="410" :ldx="-15" :ldy="-15" color="red" @mouseover="onHoverDevice('DMS')" @mouseleave="onUnhoverDevice('DMS')" :force-hover="isHovered('DMS')"/>
        <HomeDeviceSvgElement label-text="RDHT2" :x="106" :y="455" :ldx="-20" :ldy="-15" color="red" @mouseover="onHoverDevice('RDHT2')" @mouseleave="onUnhoverDevice('RDHT2')" :force-hover="isHovered('RDHT2')"/>
        <HomeDeviceSvgElement label-text="RPIR1" :x="142" :y="486" :ldx="-20" :ldy="-15" color="red" @mouseover="onHoverDevice('RPIR1')" @mouseleave="onUnhoverDevice('RPIR1')" :force-hover="isHovered('RPIR1')"/>
        <HomeDeviceSvgElement label-text="RDHT1" :x="100" :y="573" :ldx="-20" :ldy="-15" color="red" @mouseover="onHoverDevice('RDHT1')" @mouseleave="onUnhoverDevice('RDHT1')" :force-hover="isHovered('RDHT1')"/>
        <HomeDeviceSvgElement label-text="DB"    :x="250" :y="480" :ldx="-10" :ldy="-15" color="red" @mouseover="onHoverDevice('DB')" @mouseleave="onUnhoverDevice('DB')" :force-hover="isHovered('DB')"/>
        <HomeDeviceSvgElement label-text="DS1"   :x="193" :y="529" :ldx="-15" :ldy="-15" color="red" @mouseover="onHoverDevice('DS1')" @mouseleave="onUnhoverDevice('DS1')" :force-hover="isHovered('DS1')"/>
        <HomeDeviceSvgElement label-text="DUS1"  :x="192" :y="543" :ldx="-20" :ldy="-15" color="red" @mouseover="onHoverDevice('DUS1')" @mouseleave="onUnhoverDevice('DUS1')" :force-hover="isHovered('DUS1')"/>
        <HomeDeviceSvgElement label-text="DPIR1" :x="188" :y="570" :ldx="-20" :ldy="-15" color="red" @mouseover="onHoverDevice('DPIR1')" @mouseleave="onUnhoverDevice('DPIR1')" :force-hover="isHovered('DPIR1')"/>
        <HomeDeviceSvgElement label-text="DL"    :x="190" :y="600" :ldx="-10" :ldy="-15" color="red" @mouseover="onHoverDevice('DL')" @mouseleave="onUnhoverDevice('DL')" :force-hover="isHovered('DL')"/>

        <!-- PI2 -->
        <HomeDeviceSvgElement label-text="RPIR3" :x="261" :y="306" :ldx="-20" :ldy="-15" color="green" @mouseover="onHoverDevice('RPIR3')" @mouseleave="onUnhoverDevice('RPIR3')"  :force-hover="isHovered('RPIR3')"/>
        <HomeDeviceSvgElement label-text="RDHT3" :x="290" :y="306" :ldx="-15" :ldy="-15" color="green" @mouseover="onHoverDevice('RDHT3')" @mouseleave="onUnhoverDevice('RDHT3')"  :force-hover="isHovered('RDHT3')"/>
        <HomeDeviceSvgElement label-text="GSG"   :x="407" :y="334" :ldx="-20" :ldy="-15" color="green" @mouseover="onHoverDevice('GSG')" @mouseleave="onUnhoverDevice('GSG')"  :force-hover="isHovered('GSG')"/>
        <HomeDeviceSvgElement label-text="DPIR2" :x="388" :y="354" :ldx="-20" :ldy="-15" color="green" @mouseover="onHoverDevice('DPIR2')" @mouseleave="onUnhoverDevice('DPIR2')"  :force-hover="isHovered('DPIR2')"/>
        <HomeDeviceSvgElement label-text="DS2"   :x="336" :y="393" :ldx="-20" :ldy="-15" color="green" @mouseover="onHoverDevice('DS2')" @mouseleave="onUnhoverDevice('DS2')"  :force-hover="isHovered('DS2')"/>
        <HomeDeviceSvgElement label-text="DUS2"  :x="354" :y="403" :ldx="-10" :ldy="-15" color="green" @mouseover="onHoverDevice('DUS2')" @mouseleave="onUnhoverDevice('DUS2')"  :force-hover="isHovered('DUS2')"/>
        <HomeDeviceSvgElement label-text="GLCD"  :x="337" :y="426" :ldx="-15" :ldy="-15" color="green" @mouseover="onHoverDevice('GLCD')" @mouseleave="onUnhoverDevice('GLCD')"  :force-hover="isHovered('GLCD')"/>
        <HomeDeviceSvgElement label-text="GDHT"  :x="354" :y="428" :ldx="-20" :ldy="-15" color="green" @mouseover="onHoverDevice('GDHT')" @mouseleave="onUnhoverDevice('GDHT')"  :force-hover="isHovered('GDHT')"/>

        <!-- PI3 -->
        <HomeDeviceSvgElement label-text="RPIR4" :x="365"  :y="54" :ldx="-20" :ldy="-15" color="blue" @mouseover="onHoverDevice('RPIR4')" @mouseleave="onUnhoverDevice('RPIR4')"  :force-hover="isHovered('RPIR4')"/>
        <HomeDeviceSvgElement label-text="BIR"   :x="406" :y="145" :ldx="-15" :ldy="-15" color="blue" @mouseover="onHoverDevice('BIR')" @mouseleave="onUnhoverDevice('BIR')"  :force-hover="isHovered('BIR')"/>
        <HomeDeviceSvgElement label-text="RDHT4" :x="447"  :y="50" :ldx="-20" :ldy="-15" color="blue" @mouseover="onHoverDevice('RDHT4')" @mouseleave="onUnhoverDevice('RDHT4')"  :force-hover="isHovered('RDHT4')"/>
        <HomeDeviceSvgElement label-text="BRGB"  :x="498" :y="148" :ldx="-20" :ldy="-15" color="blue" @mouseover="onHoverDevice('BRGB')" @mouseleave="onUnhoverDevice('BRGB')"  :force-hover="isHovered('BRGB')"/>
        <HomeDeviceSvgElement label-text="BB"    :x="538"  :y="47" :ldx="-20" :ldy="-15" color="blue" @mouseover="onHoverDevice('BB')" @mouseleave="onUnhoverDevice('BB')"  :force-hover="isHovered('BB')"/>
        <HomeDeviceSvgElement label-text="B4SD"  :x="573"  :y="50" :ldx="-10" :ldy="-15" color="blue" @mouseover="onHoverDevice('B4SD')" @mouseleave="onUnhoverDevice('B4SD')"  :force-hover="isHovered('B4SD')"/>
    </svg>

    <span class="right">
        <template v-for="(value, key, index) in homeState.device_state">
            <div class="details-item" :class="{highlight: isHovered(key)}" @mouseover="onHoverDevice(key)" @mouseleave="onUnhoverDevice(key)">
                <HomeDeviceDetals :device="value" />
            </div>
        </template>
    </span>
</div>
</template>

<style>
.container {
    display:flex;
}

.left {
    min-width: 800px;
}

.details-item {
    display: inline-block;
    min-width: 150px;
    min-height: 150px;
    margin: 10px;
    padding: 10px;
    border: 1px solid greenyellow;
}

.highlight {
    background:beige;
    color: black; 
}
</style>