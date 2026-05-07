<template><div class="single-choice"><div v-for="(opt, i) in options" :key="i" class="option">{{ opt }}</div></div></template>
<script setup>defineProps({ options: Array, submitted: Boolean })</script>
