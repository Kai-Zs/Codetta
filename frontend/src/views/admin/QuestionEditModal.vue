<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="$emit('close')">
      <div class="bg-white dark:bg-gray-800 rounded-2xl px-6 py-6 w-[480px] max-w-[92vw] shadow-xl max-h-[85vh] overflow-y-auto">
        <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">{{ isNew ? '新增题目' : '编辑题目' }}</h3>

        <!-- 基本信息 -->
        <div class="flex gap-3 mb-3">
          <div class="flex-1">
            <label class="text-xs text-gray-400">题号</label>
            <input v-model="form.q_number" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
          </div>
          <div class="w-20">
            <label class="text-xs text-gray-400">章节</label>
            <select v-model="form.chapter" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200">
              <option v-for="c in chapters" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="w-24">
            <label class="text-xs text-gray-400">题型</label>
            <select v-model="form.type" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200">
              <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </div>

        <div class="mb-3">
          <label class="text-xs text-gray-400">标题</label>
          <input v-model="form.title" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
        </div>

        <div class="mb-3">
          <label class="text-xs text-gray-400">题干</label>
          <textarea v-model="form.content" rows="4" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200 resize-none" />
        </div>

        <!-- 单选题选项 -->
        <div v-if="form.type === '单选题'" class="mb-3">
          <label class="text-xs text-gray-400 mb-1 block">选项</label>
          <div v-for="(opt, i) in currentOptions" :key="i" class="flex gap-2 mb-1">
            <span class="text-xs text-gray-400 w-6 pt-2">{{ letters[i] }}.</span>
            <input v-model="currentOptions[i]" class="flex-1 px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
            <button @click="currentOptions.splice(i, 1)" class="text-red-400 text-xs">×</button>
          </div>
          <button @click="currentOptions.push('')" class="text-xs text-purple mt-1">+ 添加选项</button>
          <div class="mt-2 flex items-center gap-2">
            <span class="text-xs text-gray-400">正确答案：</span>
            <select v-model="form.answer" class="px-3 py-1 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded text-sm dark:text-gray-200">
              <option v-for="(_, i) in currentOptions" :key="i" :value="letters[i]">{{ letters[i] }}</option>
            </select>
          </div>
        </div>

        <!-- 判断题 -->
        <div v-if="form.type === '判断题'" class="mb-3">
          <label class="text-xs text-gray-400">正确答案：</label>
          <select v-model="form.answer" class="px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200">
            <option value="正确">正确</option>
            <option value="错误">错误</option>
          </select>
        </div>

        <!-- 填空题 -->
        <div v-if="form.type === '填空题'" class="mb-3">
          <label class="text-xs text-gray-400 mb-1 block">答案（$ 分隔多个空，如：raise$assert）</label>
          <input v-model="form.answer" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
          <p class="text-xs text-gray-400 mt-1">自动按 $ 拆分为 {{ (form.answer || '').split('$').filter(Boolean).length }} 个空</p>
        </div>

        <!-- 编程题 -->
        <div v-if="form.type === '编程题'">
          <div class="mb-3">
            <label class="text-xs text-gray-400 mb-1 block">预置代码（黑色骨架）</label>
            <textarea v-model="form.template" rows="5" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-lg text-sm font-mono resize-none" />
          </div>
          <div class="mb-3">
            <label class="text-xs text-gray-400 mb-1 block">答案代码（完整代码）</label>
            <textarea v-model="form.answer_code" rows="5" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-lg text-sm font-mono resize-none" />
          </div>
        </div>

        <!-- 备注 -->
        <div class="mb-4">
          <label class="text-xs text-gray-400 mb-1 block">备注</label>
          <input v-model="form.note" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg text-sm dark:text-gray-200" />
        </div>

        <!-- 按钮 -->
        <div class="flex gap-3">
          <button @click="$emit('close')" class="flex-1 py-2 border border-gray-200 rounded-lg text-sm">取消</button>
          <button @click="save" class="flex-1 py-2 bg-purple text-white rounded-lg text-sm font-medium">保存</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import api from '../../api'

const props = defineProps({ question: Object })
const emit = defineEmits(['close'])

const types = ['单选题', '判断题', '填空题', '编程题']
const chapters = ['1','2','3','4','5','6','7','8']
const letters = 'ABCDEFGHIJ'.split('')
const isNew = computed(() => !props.question?.id)

// 切换题型时清理旧字段
watch(() => form.type, () => {
  form.options = ''
  form.answer = ''
  form.answer_parts = ''
  form.template = ''
  form.answer_code = ''
  currentOptions.value = ['', '', '', '']
})

const currentOptions = ref([])
const form = reactive({
  q_number: '', chapter: '1', type: '单选题', title: '', content: '',
  answer: '', template: '', answer_code: '', note: '',
})

// 初始化
const q = props.question || {}
Object.keys(form).forEach(k => { if (q[k] !== undefined) form[k] = q[k] || '' })
if (form.type === '单选题') {
  try { currentOptions.value = JSON.parse(q.options || '[]') } catch { currentOptions.value = ['','','',''] }
  if (!currentOptions.value.length) currentOptions.value = ['','','','']
}

async function save() {
  const payload = { ...form }
  if (form.type === '单选题') {
    payload.options = JSON.stringify(currentOptions.value.filter(o => o.trim()))
  }
  if (form.type === '填空题') {
    const parts = (form.answer || '').split('$').filter(Boolean)
    payload.answer_parts = JSON.stringify(parts)
  }
  if (isNew.value) {
    await api.post('/admin/questions', payload)
  } else {
    await api.put(`/admin/questions/${q.id}`, payload)
  }
  emit('close')
}
</script>
