<template><Transition><div v-if="visible" class="editor-panel"><div class="editor-header">代码编辑器</div><textarea class="editor-area"></textarea></div></Transition></template>
<script setup>defineProps({ visible: Boolean, question: Object })</script>
