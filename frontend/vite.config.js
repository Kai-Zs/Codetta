import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '/codetta/',
  plugins: [vue(), tailwindcss()],
  server: { proxy: { '/api': 'http://127.0.0.1:8765' } },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/vue') || id.includes('node_modules/vue-router') || id.includes('node_modules/pinia')) {
            return 'vue-vendor'
          }
          if (id.includes('AiKpPanel') || id.includes('node_modules/marked') || id.includes('node_modules/highlight') || id.includes('node_modules/katex') || id.includes('node_modules/dompurify')) {
            return 'kp-panel'
          }
        },
      },
    },
  },
})
