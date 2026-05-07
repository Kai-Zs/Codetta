<template><Teleport to="body"><Transition><div v-if="open" class="panel-overlay"><div class="panel"><h3>设置</h3></div></div></Transition></Teleport></template>
<script setup>defineProps({ open: Boolean }); defineEmits(['close'])</script>
