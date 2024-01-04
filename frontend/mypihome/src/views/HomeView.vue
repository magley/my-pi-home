<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import axios, {isCancel, AxiosError} from 'axios';

const axiosInstance = axios.create({
    baseURL: "http://127.0.0.1:5000"
});

const isAlarm = ref(false);
const numOfPeople = ref(0);

let socket;
onMounted(() => {
    socket = new WebSocket("ws://127.0.0.1:5000/ws/alarm");
    socket.onopen = function(e) {
        console.log("Connection established");
    };

    socket.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        isAlarm.value = msg.alarm;
    };

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('[close] Connection died');
        }
    };

    socket.onerror = function(error) {
        console.log(`[error]`);
    };

    axiosInstance.get("/state").then((res) => {
        numOfPeople.value = res.data.number_of_people;
    });
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
        Alarm (websocket): <span :class="{alarm: isAlarm}">{{ isAlarm }}</span>
        <button :disabled="!isAlarm" @click="turnOffAlarm">Deactivate</button>

        <br/>
        Number of people (http axios): {{ numOfPeople }}
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