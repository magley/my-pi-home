<script setup>
const props = defineProps({
    labelText: String,
    x: Number,
    y: Number,
    ldx: Number, // X offset for the label text.
    ldy: Number, // Y offset for the label text.
    color: String, // String color "red", "green", "blue", ...
});

</script>

<template>
<g>
    <!-- This is to draw a background behind the text. Otherwise we'd use D3. -->
    <defs>
        <filter x="0" y="0" width="1" height="1" id="solid">
            <feFlood flood-color="yellow"/>
            <feComposite in="SourceGraphic" operator="xor"/>
        </filter>
    </defs>

    <circle :cx="props.x" :cy="props.y" r="7" :fill="color" />

    <text filter="url(#solid)" :x="x + ldx" :y="y + ldy"> {{labelText}} </text>
    <text :x="x + ldx" :y="y + ldy">{{labelText}}</text>
</g>
</template>

<style>
svg text {
    display: none;
}
svg g:hover text {
    display: block;
}

</style>