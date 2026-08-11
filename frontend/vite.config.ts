import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/** 开发构建配置：React，并把 /api 请求代理到本地 FastAPI。 */
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': process.env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000',
    },
  },
})
