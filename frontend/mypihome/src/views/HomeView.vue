<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import axios, {isCancel, AxiosError} from 'axios';
import HomeBlueprint from '@/components/HomeBlueprint.vue';

const axiosInstance = axios.create({
    baseURL: "http://127.0.0.1:5000"
});

const isAlarm = ref(false);

let socket;
onMounted(() => {
    socket = new WebSocket("ws://127.0.0.1:5000/ws/alarm");
    socket.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        isAlarm.value = msg.alarm;
    };
    socket.onerror = function(error) {
        console.error(error);
    };
});

onUnmounted(() => {
    socket.close();
});

const turnOffAlarm = () => {
    axiosInstance.post("/alarm", {"alarm": false});
}

</script>

<template>

<h1>
    MyPiHome
</h1>

<div>
    <p>
        Alarm: <span :class="{alarm: isAlarm}">{{ isAlarm }}</span>
        <button :disabled="!isAlarm" @click="turnOffAlarm">Deactivate</button>
    </p>

    <p>
        <HomeBlueprint/>
    </p>
</div>
</template>

<style>
.alarm {
    background-color: red;
    font-weight: bolder;
    animation: blink 0.5s infinite;
}

@keyframes blink {
  from { color: white; }
  to { color: black; }
}
</style>