<template><Teleport to="body"><Transition><div v-if="open" class="modal-overlay"><div class="modal"><h3>筛选</h3><slot /></div></div></Transition></Teleport></template>
<script setup>defineProps({ open: Boolean }); defineEmits(['close'])</script>
