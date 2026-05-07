<template><div class="fill-blank"><input v-for="(_, i) in blanks" :key="i" class="blank-input" /></div></template>
<script setup>defineProps({ blanks: Array, submitted: Boolean })</script>
