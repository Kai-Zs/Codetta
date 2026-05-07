<template><Teleport to="body"><Transition><div v-if="open" class="sheet-overlay"><div class="sheet"><div v-for="item in items" :key="item.id" class="sheet-dot">{{ item.label }}</div></div></div></Transition></Teleport></template>
<script setup>defineProps({ open: Boolean, items: Array, currentId: [Number, null] }); defineEmits(['close', 'jump'])</script>
