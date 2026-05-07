<template><Teleport to="body"><Transition><div v-if="visible" class="toast">{{ msg }}</div></Transition></Teleport></template>
<script setup>defineProps({ visible: Boolean, msg: String })</script>
