/**
 * CampusAssetManager/frontend/src/App.vue
 * 应用根组件
 *
 * 功能说明：
 * - 集成通用布局组件
 * - 提供路由视图
 * - 处理全局样式
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/stores'

/**
 * 应用状态管理
 */
const appStore = useAppStore()

/**
 * 组件挂载时初始化设备类型
 */
onMounted(() => {
  appStore.initDevice()
  
  /**
   * 监听窗口大小变化
   * 自动切换设备类型
   */
  window.addEventListener('resize', appStore.initDevice)
})
</script>

<template>
  <router-view />
</template>

<style>
/**
 * 全局样式重置
 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/**
 * 滚动条样式
 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background-color: rgba(144, 147, 153, 0.5);
}

::-webkit-scrollbar-track {
  background-color: transparent;
}
</style>
