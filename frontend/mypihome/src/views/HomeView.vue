<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import axios, {isCancel, AxiosError} from 'axios';
import HomeBlueprint from '@/components/HomeBlueprint.vue';

const axiosInstance = axios.create({
    baseURL: "http://127.0.0.1:5000"
});

const isAlarm = ref(false);
const isSecurity = ref(false);

const wakeupTime = ref("");
const wakeupTimeInput = ref(null);
const isWakeupActive = ref(false);

let socket;
let socket2;
let socket3;
onMounted(() => {
    socket = new WebSocket("ws://127.0.0.1:5000/ws/alarm");
    socket.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        isAlarm.value = msg.alarm;
    };
    socket.onerror = function(error) {
        console.error(error);
    };

    socket2 = new WebSocket("ws://127.0.0.1:5000/ws/wakeup");
    socket2.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        if (msg.is_wakeup_active !== undefined) {
            isWakeupActive.value = msg.is_wakeup_active;
        }
        if (msg.wakeup !== undefined) {
            wakeupTime.value = msg.wakeup;
        }
    };
    socket2.onerror = function(error) {
        console.error(error);
    };

    socket3 = new WebSocket("ws://127.0.0.1:5000/ws/security");
    socket3.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        isSecurity.value = msg.security_active;
    };
    socket3.onerror = function(error) {
        console.error(error);
    };
});

onUnmounted(() => {
    socket.close();
});

const turnOffAlarm = () => {
    axiosInstance.post("/alarm", {"alarm": false});
}

const setWakeup = (val) => {
    axiosInstance.post("/wakeup", {"wakeup": val});
    wakeupTime.value = val;
    wakeupTimeInput.value.value = "";
}

const clearWakeup = () => {
    axiosInstance.post("/wakeup", {"wakeup": ""});
    wakeupTime.value = "";
}

const turnOffWakeup = () => {
    axiosInstance.post("/is_wakeup_active", {"is_wakeup_active": false})
}

const RGBColorInput = ref(null);
const setRGBColor = (val) => {
    axiosInstance.post("/brgb", {"rgb": val});
    RGBColorInput.value.value = "";
}

const disableRGB = _ => {
    setRGBColor("000");
}

</script>

<template>

<h1>
    MyPiHome
</h1>

<div>
    <div class="controls">
        <p>
            Alarm: <span :class="{alarm: isAlarm}">{{ isAlarm }}</span>
            <button :disabled="!isAlarm" @click="turnOffAlarm">Deactivate</button>
            <br />
            Security: {{ isSecurity }}
        </p>
        <div class="wakeup">
            Wakeup time:
            <template v-if="wakeupTime != ''">
            {{ wakeupTime }}
            </template>
            <template v-else>None</template>
            <br/>
            <form @submit.prevent="() => setWakeup(wakeupTimeInput.value)" style="display: inline;">
                <!-- Regex pattern: https://stackoverflow.com/a/7536768 -->
                <input
                    ref="wakeupTimeInput"
                    type="text"
                    required
                    maxlength="5"
                    placeholder="00:00"
                    pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$" 
                    title="HH:MM"
                    style="width: 3rem;">
                <input type="submit" value="Set">
            </form>
            <button @click="clearWakeup">Clear</button>
            <p>
                Wakeup: <span :class="{alarm: isWakeupActive}">{{ isWakeupActive }}</span>
                <button :disabled="!isWakeupActive" @click="turnOffWakeup">Deactivate</button>
            </p>
        </div>
        <div>
            BRGB color
            <br />
            <form @submit.prevent="() => setRGBColor(RGBColorInput.value)" style="display: inline;">
                <!-- Regex pattern: https://stackoverflow.com/a/7536768 -->
                <input
                    ref="RGBColorInput"
                    type="text"
                    required
                    maxlength="3"
                    placeholder="101"
                    pattern="^(0|1)(0|1)(0|1)" 
                    title="(0|1)(0|1)(0|1)"
                    style="width: 3rem;">
                <input type="submit" value="Set">
            </form>
            <button @click="disableRGB">Disable</button>
        </div>
    </div>

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

.controls {
    display: flex;
    flex-direction: row;
    gap: 3rem;
}

@keyframes blink {
  from { color: white; }
  to { color: black; }
}
</style>