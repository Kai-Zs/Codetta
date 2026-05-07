<template><Teleport to="body"><Transition><div v-if="open" class="dialog-overlay"><div class="dialog"><p>{{ msg }}</p><button @click="$emit('confirm')">确认</button><button @click="$emit('close')">取消</button></div></div></Transition></Teleport></template>
<script setup>defineProps({ open: Boolean, msg: String }); defineEmits(['confirm', 'close'])</script>
