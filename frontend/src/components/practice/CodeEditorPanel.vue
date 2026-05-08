<template>
  <Teleport to="body" :disabled="isMobile">
    <Transition enter-active-class="transition duration-300 ease-out" leave-active-class="transition duration-200 ease-in"
      enter-from-class="opacity-0 translate-x-5" leave-to-class="opacity-0 translate-x-5">
      <div v-if="visible" :class="['editor-panel', { 'editor-panel--mobile': isMobile }]">
        <div class="editor-header">
          <h2>代码编辑器</h2>
          <span class="text-xs text-purple bg-purple/5 px-2 py-1 rounded">Python</span>
        </div>
        <div class="editor-body">
          <div ref="editorHost" class="editor-area"></div>
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
import { ref, watch, onBeforeUnmount, nextTick } from 'vue'
import { EditorView, keymap, lineNumbers, highlightActiveLine } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { defaultKeymap, indentWithTab } from '@codemirror/commands'
import { useThemeStore } from '../../stores/theme'

const props = defineProps({ visible: Boolean, question: Object, previousAnswer: Object })
const emit = defineEmits(['submit'])

const theme = useThemeStore()
const editorHost = ref(null)
const isMobile = ref(window.innerWidth <= 768)
let view = null

function onResize() { isMobile.value = window.innerWidth <= 768 }
window.addEventListener('resize', onResize)

function getExtensions(dark) {
  return [
    python(),
    lineNumbers(),
    highlightActiveLine(),
    keymap.of([...defaultKeymap, indentWithTab]),
    dark ? oneDark : [],
    EditorView.theme({
      '&': { height: '100%' },
      '.cm-scroller': { overflow: 'auto', fontFamily: "'JetBrains Mono','Fira Code',Consolas,monospace", fontSize: '13px', lineHeight: '1.7' },
      '.cm-content': { padding: '16px' },
      '.cm-gutters': dark ? { background: '#1a1a2e', color: '#5a5a7e', border: 'none' } : { background: '#f8f6ff', color: '#a0a0c0', border: 'none' },
      '.cm-activeLineGutter': { background: dark ? '#222236' : '#ece6ff' },
    }, { dark }),
  ]
}

function createEditor() {
  if (!editorHost.value || view) return
  const dark = theme.isDark
  const code = props.previousAnswer?.code || getTemplate()
  view = new EditorView({
    state: EditorState.create({
      doc: code,
      extensions: getExtensions(dark),
    }),
    parent: editorHost.value,
  })
}

function destroyEditor() {
  if (view) { view.destroy(); view = null }
}

function getTemplate() {
  return props.question?.template || ''
}

function getCode() {
  return view ? view.state.doc.toString() : ''
}

function reset() {
  if (!view) return
  view.dispatch({
    changes: { from: 0, to: view.state.doc.length, insert: getTemplate() },
  })
}

function submit() {
  emit('submit', getCode())
}

watch(() => props.visible, async (v) => {
  if (v) { await nextTick(); createEditor() }
  else destroyEditor()
})

watch(() => props.question, () => {
  if (!view || !props.visible) return
  const code = props.previousAnswer?.code || getTemplate()
  if (view.state.doc.toString() !== code) {
    view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: code } })
  }
})

watch(() => theme.isDark, (dark) => {
  if (!view) return
  view.dispatch({ effects: EditorView.reconfigure.of(getExtensions(dark)) })
})

onBeforeUnmount(() => {
  destroyEditor()
  window.removeEventListener('resize', onResize)
})

defineExpose({ getCode, reset })
</script>
