<script setup>
import HomeDeviceSvgElement from './HomeDeviceSvgElement.vue';

</script>

<template>
<svg width="800" height="800" xmlns="http://www.w3.org/2000/svg">
    <image href="../../public/home.png" />

    <!-- PI1 -->
    <HomeDeviceSvgElement label-text="RPIR2" :x= "95" :y="305" :ldx="-20" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="DMS"   :x="190" :y="410" :ldx="-15" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="RDTH2" :x="106" :y="455" :ldx="-20" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="RPIR1" :x="142" :y="486" :ldx="-20" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="RDHT1" :x="100" :y="573" :ldx="-20" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="DB"    :x="250" :y="480" :ldx="-10" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="DS1"   :x="193" :y="529" :ldx="-15" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="DUS1"  :x="192" :y="543" :ldx="-20" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="DPIR1" :x="188" :y="570" :ldx="-20" :ldy="-15" color="red" />
    <HomeDeviceSvgElement label-text="DL"    :x="190" :y="600" :ldx="-10" :ldy="-15" color="red" />

    <!-- PI2 -->
    <HomeDeviceSvgElement label-text="RPIR3" :x="261" :y="306" :ldx="-20" :ldy="-15" color="green" />
    <HomeDeviceSvgElement label-text="RDHT3" :x="290" :y="306" :ldx="-15" :ldy="-15" color="green" />
    <HomeDeviceSvgElement label-text="GSG"   :x="407" :y="334" :ldx="-20" :ldy="-15" color="green" />
    <HomeDeviceSvgElement label-text="DPIR2" :x="388" :y="354" :ldx="-20" :ldy="-15" color="green" />
    <HomeDeviceSvgElement label-text="DS2"   :x="336" :y="393" :ldx="-20" :ldy="-15" color="green" />
    <HomeDeviceSvgElement label-text="DUS2"  :x="354" :y="403" :ldx="-10" :ldy="-15" color="green" />
    <HomeDeviceSvgElement label-text="GLCD"  :x="337" :y="426" :ldx="-15" :ldy="-15" color="green" />
    <HomeDeviceSvgElement label-text="GDHT"  :x="354" :y="428" :ldx="-20" :ldy="-15" color="green" />

    <!-- PI3 -->
    <HomeDeviceSvgElement label-text="RPIR4" :x="365" :y="54" :ldx="-20" :ldy="-15" color="blue" />
    <HomeDeviceSvgElement label-text="BIR"   :x="406" :y="145" :ldx="-15" :ldy="-15" color="blue" />
    <HomeDeviceSvgElement label-text="RDHT4" :x="447" :y="50" :ldx="-20" :ldy="-15" color="blue" />
    <HomeDeviceSvgElement label-text="BRGB"  :x="498" :y="148" :ldx="-20" :ldy="-15" color="blue" />
    <HomeDeviceSvgElement label-text="BB"    :x="538" :y="47" :ldx="-20" :ldy="-15" color="blue" />
    <HomeDeviceSvgElement label-text="B4SD"  :x="573" :y="50" :ldx="-10" :ldy="-15" color="blue" />
</svg>
</template>