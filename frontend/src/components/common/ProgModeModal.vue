<template><Teleport to="body"><Transition><div v-if="open" class="modal-overlay"><div class="modal"><h3>编程题模式</h3><button>动手写代码</button><button>先看思路</button></div></div></Transition></Teleport></template>
<script setup>defineProps({ open: Boolean }); defineEmits(['close'])</script>
