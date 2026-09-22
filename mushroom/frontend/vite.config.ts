import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {
      // 학생용 API
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      // 관리자 페이지
      '/admins': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})