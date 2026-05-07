<template>
  <Teleport to="body">
    <Transition enter-active-class="transition duration-300 ease-out" leave-active-class="transition duration-200 ease-in"
      enter-from-class="opacity-0 translate-x-5" leave-to-class="opacity-0 translate-x-5">
      <div v-if="visible" class="editor-panel">
        <div class="editor-header">
          <h2>代码编辑器</h2>
          <span class="text-xs text-purple bg-purple/5 px-2 py-1 rounded">Python</span>
        </div>
        <div class="editor-body">
          <textarea
            ref="ta"
            v-model="code"
            class="editor-area"
            spellcheck="false"
            placeholder="在这里编写代码..."></textarea>
        </div>
        <div class="editor-footer">
          <button @click="reset" class="text-sm text-gray-400 hover:text-gray-600 transition">重置</button>
          <button @click="submit" class="px-5 py-2 bg-purple text-white rounded-lg text-sm font-medium">提交判题</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({ visible: Boolean, question: Object })
const emit = defineEmits(['submit'])

const ta = ref(null)
const code = ref('')

const templateCode = computed(() => {
  if (!props.question) return ''
  const t = props.question.template
  return t || ''
})

watch(() => props.question, () => {
  code.value = templateCode.value
}, { immediate: true })

function getCode() { return code.value }
function reset() { code.value = templateCode.value }

function submit() {
  emit('submit', code.value)
}

defineExpose({ getCode, reset })
</script>
