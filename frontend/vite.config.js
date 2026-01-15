/**
 * CampusAssetManager/frontend/vite.config.js
 * Vite 配置文件
 *
 * 功能说明：
 * - 配置 Vue 3 插件
 * - 配置 Element Plus 自动导入
 * - 配置 CSS 预处理器
 * - 配置代理服务
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

/**
 * Vite 配置对象
 */
export default defineConfig({
  plugins: [vue()],
  css: {
    postcss: './postcss.config.js'
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0', // 允许局域网访问
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
