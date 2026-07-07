import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      host: '0.0.0.0',
      port: 40003,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://interview-tiger-backend:8000',
          changeOrigin: true
        }
      }
    }
  }
})
